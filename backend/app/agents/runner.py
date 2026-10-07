import time

from sqlalchemy.orm import Session

from app.agents.composer import LOC
from app.agents.graph import GRAPH
from app.agents.state import AgentContext
from app.agents.tools import AgentTools
from app.database.repositories import HistoryRepository, UserRepository
from app.services.cache_service import CacheService, get_cache
from app.services.metrics import metrics
from app.services.product_service import ProductService

MAX_MESSAGE_LENGTH = 1000


def run_agent(db: Session, session_id: str, message: str, cache: CacheService | None = None) -> dict:
    started = time.perf_counter()
    cache = cache or get_cache()
    tools = AgentTools(db)
    ctx = AgentContext(db=db, tools=tools, products=ProductService(db), cache=cache)
    state = GRAPH.invoke(
        {"session_id": session_id, "message": message, "notes": [], "trace": [], "error": None},
        config={"configurable": {"ctx": ctx}},
    )
    lang = state.get("language") or "en"
    reply = state.get("reply")
    payload = state.get("payload")
    if not reply:
        reply = LOC[lang]["db_error"] if state.get("error") == "db" else LOC[lang]["error"]
        payload = {"type": "error", "cards": [], "compared_ids": [], "notes": []}
    elapsed = time.perf_counter() - started
    cache_hit = bool(state.get("cache_hit"))
    metrics.record(elapsed * 1000, cache_hit, tools.timings.get("rag_ms", 0.0), ctx.timings.get("llm_ms", 0.0))
    return {
        "reply": reply,
        "payload": payload,
        "intent": state.get("intent"),
        "category": state.get("category"),
        "preferences": state.get("preferences"),
        "cache_hit": cache_hit,
        "error": state.get("error"),
        "trace": state.get("trace", []),
        "response_time": round(elapsed, 4),
        "timings": {"rag_ms": round(tools.timings.get("rag_ms", 0.0), 2), "llm_ms": round(ctx.timings.get("llm_ms", 0.0), 2)},
    }


def handle_chat(db: Session, session_id: str, message: str, cache: CacheService | None = None) -> dict:
    users = UserRepository(db)
    history = HistoryRepository(db)
    user = users.get_or_create(session_id)
    users.add_message(user.id, "user", message)
    result = run_agent(db, session_id, message, cache)
    users.add_message(user.id, "assistant", result["reply"], result["payload"])
    prefs = result.get("preferences") or {}
    brands = prefs.get("preferred_brands") or []
    if result["intent"] in {"recommend", "compare", "reviews", "shopping_list"} and not result["error"]:
        history.add_search(user.id, message, result.get("category"), brands[0] if brands else None, result["intent"], result["response_time"], result["cache_hit"])
    payload = result["payload"] or {}
    if payload.get("type") in {"recommend", "compare", "shopping_list"} and payload.get("compared_ids"):
        history.add_comparison(user.id, payload["compared_ids"], payload.get("winner_id"))
    return result
