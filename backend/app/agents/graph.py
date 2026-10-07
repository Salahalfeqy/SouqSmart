import logging

from langgraph.graph import END, START, StateGraph
from sqlalchemy.exc import SQLAlchemyError

from app.agents import composer, llm
from app.agents.composer import LOC
from app.agents.state import AgentContext, AgentState
from app.services.cache_service import CacheService
from app.services.requirement_service import Requirements, extract_requirements, normalize
from app.services.scoring_service import feature_match

logger = logging.getLogger("souqsmart.agent")

CACHEABLE = {"recommend", "compare", "reviews", "shopping_list"}


def ctx_of(config) -> AgentContext:
    return config["configurable"]["ctx"]


def safe(name):
    def decorator(fn):
        def wrapper(state, config):
            try:
                return fn(state, config)
            except SQLAlchemyError as exc:
                logger.exception("node %s db failure", name)
                return {"error": "db", "trace": [f"{name}:error:{type(exc).__name__}"]}
            except Exception as exc:
                logger.exception("node %s failed", name)
                return {"error": "unknown", "trace": [f"{name}:error:{type(exc).__name__}"]}

        wrapper.__name__ = name
        return wrapper

    return decorator


@safe("load_preferences")
def load_preferences(state, config):
    ctx = ctx_of(config)
    prefs = ctx.tools.get_user_preferences(state["session_id"])
    return {"preferences": prefs, "trace": ["tool:get_user_preferences"]}


@safe("understand")
def understand(state, config):
    ctx = ctx_of(config)
    req = extract_requirements(state["message"], ctx.products, state.get("preferences"))
    if llm.enabled() and req.intent in {"recommend", "clarify", "shopping_list"}:
        data = llm.extract_requirements(state["message"])
        if data:
            if data.get("category") and data["category"] in LOC["en"]["categories"] and data["category"] not in req.categories:
                req.categories.insert(0, data["category"])
            if isinstance(data.get("budget"), (int, float)) and req.budget is None and data["budget"] > 0:
                req.budget = float(data["budget"])
            for key, attr in (("brands", "brands"), ("priorities", "priorities"), ("must_have", "must_have")):
                for v in data.get(key) or []:
                    if isinstance(v, str) and v not in getattr(req, attr):
                        getattr(req, attr).append(v)
            if req.intent == "clarify" and (req.categories or req.budget):
                req.intent = "recommend"
    return {"requirements": req.to_dict(), "intent": req.intent, "language": req.language, "trace": [f"understand:{req.intent}"]}


@safe("remember")
def remember(state, config):
    ctx = ctx_of(config)
    req = Requirements(**state["requirements"])
    prefs = ctx.tools.preferences.merge_requirements(state["session_id"], req)
    category = req.categories[0] if req.categories else (prefs["preferred_categories"][0] if prefs["preferred_categories"] else None)
    lang = state["language"]
    clarify = None
    intent = state["intent"]
    if intent == "recommend":
        if not category:
            clarify = "ask_category"
        elif not prefs.get("budget") and not req.no_budget:
            clarify = "ask_budget"
    elif intent == "greeting":
        clarify = "greeting"
    elif intent == "clarify":
        clarify = "clarify" if not (prefs["preferred_categories"] or prefs.get("budget")) else "ask_category"
    elif intent == "reset":
        clarify = "reset"
    return {"preferences": prefs, "category": category, "clarify": clarify, "trace": ["tool:save_preferences"]}


def gate(state):
    if state.get("error"):
        return "fail"
    return "simple_reply" if state.get("clarify") else "check_cache"


@safe("simple_reply")
def simple_reply(state, config):
    lang = state["language"]
    loc = LOC[lang]
    key = state["clarify"]
    text = loc[key]
    if key == "ask_budget":
        text = text.format(category=loc["categories"].get(state["category"], state["category"]))
    return {"reply": text, "payload": {"type": "message", "cards": [], "compared_ids": [], "notes": []}, "trace": [f"reply:{key}"]}


def cache_payload(state):
    req = state["requirements"]
    prefs = state["preferences"]
    body = {
        "intent": state["intent"],
        "lang": state["language"],
        "category": state.get("category"),
        "budget": prefs.get("budget") if state["intent"] in {"recommend", "shopping_list"} else None,
        "min_price": req.get("min_price"),
        "brands": sorted(prefs.get("preferred_brands") or []) if state["intent"] in {"recommend", "shopping_list"} else [],
        "priorities": sorted(prefs.get("priority_features") or []),
        "must_have": sorted(prefs.get("must_have_features") or []),
        "names": sorted(req.get("product_names") or []),
        "categories": sorted(req.get("categories") or []),
    }
    if state["intent"] in {"reviews", "compare"}:
        body["query"] = normalize(state["message"])
        body["history_dependent"] = not req.get("product_names")
    return body


@safe("check_cache")
def check_cache(state, config):
    ctx = ctx_of(config)
    body = cache_payload(state)
    if body.get("history_dependent"):
        return {"cache_key": None, "cache_hit": False, "trace": ["cache:skip"]}
    key = CacheService.make_key("chat", body)
    hit = ctx.cache.get(key)
    if hit is not None:
        return {"cache_key": key, "cache_hit": True, "reply": hit["reply"], "payload": hit["payload"], "trace": ["cache:hit"]}
    return {"cache_key": key, "cache_hit": False, "trace": ["cache:miss"]}


def after_cache(state):
    if state.get("error"):
        return "fail"
    if state.get("cache_hit"):
        return "done"
    return {"recommend": "search", "compare": "resolve", "reviews": "resolve", "shopping_list": "build_list"}[state["intent"]]


@safe("search")
def search(state, config):
    ctx = ctx_of(config)
    prefs, req = state["preferences"], state["requirements"]
    category = state["category"]
    brands = prefs.get("preferred_brands") or []
    budget = prefs.get("budget")
    min_price = req.get("min_price")
    notes, trace = [], []

    def run(brands_, max_price):
        found = ctx.tools.search_products(category=category, brand=brands_, min_price=min_price, max_price=max_price)
        found = ctx.tools.filter_products(found, category=category, brands=brands_, min_price=min_price, max_price=max_price)
        return found

    found = run(brands, budget)
    trace.append("tool:search_products")
    must = prefs.get("must_have_features") or []
    if must:
        strict = [p for p in found if all(feature_match(p, f) for f in must)]
        found = strict or found
    if not found and brands:
        found = run([], budget)
        if found:
            notes.append("brand_relaxed")
    if not found and budget:
        pool = run([], None)
        pool = sorted([p for p in pool if p["price"] > budget], key=lambda p: p["price"])[:5]
        if pool:
            found = pool
            notes.append("over_budget")
    if not found:
        semantic = ctx.tools.semantic_search(state["message"], category=category, brands=brands or None, max_price=budget)
        found = ctx.tools.filter_products(semantic, require_price=True)
        if found:
            notes.append("semantic")
        trace.append("tool:semantic_search")
    return {"candidates": found, "notes": notes, "trace": trace}


@safe("score_rank")
def score_rank(state, config):
    ctx = ctx_of(config)
    if not state["candidates"]:
        return {"ranked": [], "product_ids": [], "trace": ["tool:calculate_value_score"]}
    prefs = dict(state["preferences"])
    if "over_budget" in state.get("notes", []):
        prefs["budget"] = None
    ranked = [r for r in ctx.tools.calculate_value_score(state["candidates"], prefs) if r["scored"]]
    return {"ranked": ranked, "product_ids": [r["id"] for r in ranked[:3]], "trace": ["tool:calculate_value_score"]}


def after_score(state):
    if state.get("error"):
        return "fail"
    return "compare" if state.get("ranked") else "respond"


@safe("resolve")
def resolve(state, config):
    ctx = ctx_of(config)
    ids = list(state["requirements"].get("product_names") or [])
    if not ids:
        for msg in reversed(ctx.tools.users.messages(ctx.tools.users.get_or_create(state["session_id"]).id, limit=50)):
            if msg.role == "assistant" and msg.payload and msg.payload.get("compared_ids"):
                ids = list(msg.payload["compared_ids"])
                break
    update = {"product_ids": ids, "trace": ["resolve_products"]}
    if ids and state["intent"] == "reviews":
        from app.services.comparison_service import SPEC_LABELS

        items = ctx.products.get_many(ids)
        if items:
            update["comparison"] = {"category": items[0]["category"], "products": items, "winner_id": None, "notes": [], "spec_keys": SPEC_LABELS.get(items[0]["category"], [])}
            update["product_ids"] = [p["id"] for p in items]
        else:
            update["product_ids"] = []
    return update


def after_resolve(state):
    if state.get("error"):
        return "fail"
    if not state.get("product_ids"):
        return "respond"
    return "compare" if state["intent"] == "compare" else "reviews"


@safe("compare")
def compare(state, config):
    ctx = ctx_of(config)
    prefs = state["preferences"]
    ranked = state.get("ranked") or []
    if state["intent"] == "recommend" and len(ranked) >= 3:
        from app.services.comparison_service import SPEC_LABELS

        top = ranked[:3]
        comparison = {"category": top[0]["category"], "products": top, "winner_id": top[0]["id"], "notes": [], "spec_keys": SPEC_LABELS.get(top[0]["category"], [])}
    else:
        comparison = ctx.tools.compare_products(state["product_ids"], prefs, min_items=3)
    notes = list(comparison.get("notes", []))
    return {"comparison": comparison, "notes": notes, "product_ids": [p["id"] for p in comparison["products"]], "trace": ["tool:compare_products"]}


def after_compare(state):
    if state.get("error"):
        return "fail"
    if not state["comparison"]["products"]:
        return "respond"
    return "reviews"


@safe("reviews")
def reviews(state, config):
    ctx = ctx_of(config)
    prefs = state["preferences"]
    query = " ".join([state["message"]] + (prefs.get("priority_features") or []))
    ids = state["product_ids"][:3]
    found, degraded = ctx.tools.retrieve_reviews(query, ids, 2, state["language"])
    notes = ["rag_degraded"] if degraded else []
    return {"reviews": {str(k): v for k, v in found.items()}, "notes": notes, "trace": ["tool:retrieve_reviews"]}


@safe("build_list")
def build_list(state, config):
    ctx = ctx_of(config)
    req = state["requirements"]
    prefs = state["preferences"]
    categories = req.get("categories") or prefs.get("preferred_categories") or []
    result = ctx.tools.build_shopping_list(categories, prefs.get("budget"), prefs)
    return {"shopping_list": result, "trace": ["tool:build_shopping_list"]}


def names_of(state):
    out = {}
    for p in (state.get("comparison") or {}).get("products", []):
        out[p["id"]] = p["name"]
    return out


@safe("respond")
def respond(state, config):
    ctx = ctx_of(config)
    lang = state["language"]
    loc = LOC[lang]
    prefs = state["preferences"]
    intent = state["intent"]
    category = state.get("category")
    notes = list(dict.fromkeys(state.get("notes", [])))
    payload = {"type": intent, "cards": [], "compared_ids": [], "winner_id": None, "notes": []}

    if intent == "shopping_list":
        sl = state["shopping_list"]
        lines = [f"**{loc['list_title']}**"]
        cards = []
        for it in sl["items"]:
            cname = loc["categories"].get(it["category"], it["category"])
            if it["product"]:
                p = it["product"]
                lines.append(f"- {cname}: **{p['name']}** — {composer.fmt_price(p['price'], lang)}")
                cards.append(composer.card(p, [], lang))
            else:
                lines.append(f"- {cname}: " + loc["list_none"].format(name=it["cheapest_name"], price=composer.fmt_price(it["cheapest_price"], lang)))
        if not sl["items"]:
            lines.append(loc["no_results"])
        else:
            lines.append("\n" + loc["list_total"].format(total=composer.fmt_price(sl["total"], lang)))
            if sl.get("remaining") is not None:
                lines.append(loc["list_remaining"].format(amount=composer.fmt_price(max(sl["remaining"], 0), lang)))
        if sl["missing"]:
            lines.append(loc["list_missing"].format(items=", ".join(sl["missing"])))
        payload.update(cards=cards, compared_ids=[c["id"] for c in cards], shopping_total=sl["total"])
        return {"reply": "\n".join(lines), "payload": payload, "trace": ["reply:shopping_list"]}

    if intent in {"compare", "reviews"} and not state.get("product_ids"):
        key = "need_products" if intent == "compare" else "need_product_reviews"
        payload["type"] = "message"
        return {"reply": loc[key], "payload": payload, "trace": ["reply:need_products"]}

    if intent == "recommend" and not state.get("ranked"):
        payload["type"] = "message"
        return {"reply": loc["no_results"], "payload": payload, "trace": ["reply:no_results"]}

    comparison = state["comparison"]
    products = comparison["products"]
    winner = next((p for p in products if p["id"] == comparison["winner_id"]), products[0] if products else None)
    if intent == "reviews":
        payload["winner_id"] = None
    review_map = state.get("reviews", {})
    others = [p for p in products if winner and p["id"] != winner["id"]]
    cards = []
    for p in products:
        reasons = composer.winner_reasons(p, [o for o in products if o["id"] != p["id"]], prefs, lang) if winner and p["id"] == winner["id"] else []
        cards.append(composer.card(p, comparison["spec_keys"], lang, reasons, review_map.get(str(p["id"]), [])))
    names = names_of(state)
    note_lines = composer.render_notes(notes + comparison.get("notes", []), lang, names, category)
    lines = []

    if intent == "reviews":
        lines.append(f"**{loc['reviews_title']}**")
        for c in cards:
            lines.append(f"\n**{c['name']}** — {loc['rating']} {c['rating']}/5")
            if c["reviews"]:
                lines += [f"- {composer.quote(r)}" for r in c["reviews"]]
            else:
                lines.append(f"- {loc['no_reviews']}")
    else:
        if intent == "recommend":
            wc = next(c for c in cards if c["id"] == winner["id"])
            summary = composer.summary_text(category, prefs, lang)
            price_text = wc["price_text"]
            lines.append(loc["top_pick"].format(summary=summary, name=winner["name"], price=price_text, score=winner["value_score"]))
        else:
            lines.append(f"**{loc['compare_title']}**")
            if winner:
                lines.append(loc["verdict"].format(name=winner["name"]))
        wc = next(c for c in cards if c["id"] == winner["id"])
        reasons_text = None
        if llm.enabled():
            allowed = {int(p["price"]) for p in products if p["price"] is not None} | ({int(prefs["budget"])} if prefs.get("budget") else set())
            facts = {"top_pick": winner["name"], "brand": winner["brand"], "priorities": prefs.get("priority_features"), "reasons": wc["reasons"], "rating": winner["rating"]}
            reasons_text, ms = llm.explain(facts, state["message"], allowed)
            ctx.timings["llm_ms"] = ctx.timings.get("llm_ms", 0) + ms
        if reasons_text:
            lines.append(reasons_text)
        else:
            lines.append(f"\n**{loc['why']}** " + "، ".join(wc["reasons"]) if lang == "ar" else f"\n**{loc['why']}** " + "; ".join(wc["reasons"]))
        lines.append(f"\n**{loc['compared']}**")
        lines.append(composer.markdown_table(cards, lang))
        quotes = [(c["name"], r) for c in cards if c["id"] == winner["id"] for r in c["reviews"][:2]]
        if quotes:
            lines.append(f"\n**{loc['shoppers']}**")
            lines += [f"- {composer.quote(r)}" for _, r in quotes]
    for n in note_lines:
        lines.append(f"\n> {n}")
    if intent == "recommend":
        lines.append(f"\n{loc['next']}")
    payload.update(cards=cards, compared_ids=[c["id"] for c in cards], winner_id=winner["id"] if winner else None, notes=note_lines)
    return {"reply": "\n".join(lines), "payload": payload, "trace": [f"reply:{intent}"]}


@safe("store_cache")
def store_cache(state, config):
    ctx = ctx_of(config)
    key = state.get("cache_key")
    degraded = any(n in state.get("notes", []) for n in ("rag_degraded",))
    if key and state["payload"].get("type") not in {"message"} and not degraded:
        ctx.cache.set(key, {"reply": state["reply"], "payload": state["payload"]})
        return {"trace": ["cache:store"]}
    return {"trace": ["cache:skip_store"]}


def fail(state, config):
    loc = LOC[state.get("language") or "en"]
    text = loc["db_error"] if state.get("error") == "db" else loc["error"]
    return {"reply": text, "payload": {"type": "error", "cards": [], "compared_ids": [], "notes": []}, "trace": ["reply:error"]}


def link(builder, src, mapping_fn, targets):
    builder.add_conditional_edges(src, mapping_fn, {t: t for t in targets} | {"fail": "fail"})


def build_graph():
    g = StateGraph(AgentState)
    for name, fn in [
        ("load_preferences", load_preferences), ("understand", understand), ("remember", remember), ("simple_reply", simple_reply),
        ("check_cache", check_cache), ("search", search), ("score_rank", score_rank), ("resolve", resolve), ("compare", compare),
        ("reviews", reviews), ("build_list", build_list), ("respond", respond), ("store_cache", store_cache), ("fail", fail),
    ]:
        g.add_node(name, fn)

    def ok(nxt):
        return lambda s: "fail" if s.get("error") else nxt

    g.add_edge(START, "load_preferences")
    for src, nxt in [("load_preferences", "understand"), ("understand", "remember"), ("search", "score_rank"), ("reviews", "respond"),
                     ("build_list", "respond"), ("respond", "store_cache"), ("simple_reply", END), ("store_cache", END)]:
        if nxt == END:
            g.add_edge(src, END)
        else:
            link(g, src, ok(nxt), [nxt])
    link(g, "remember", gate, ["simple_reply", "check_cache"])
    link(g, "check_cache", lambda s: after_cache(s), ["search", "resolve", "build_list", "done"])
    g.add_node("done", lambda s: {})
    g.add_edge("done", END)
    link(g, "score_rank", after_score, ["compare", "respond"])
    link(g, "resolve", after_resolve, ["compare", "reviews", "respond"])
    link(g, "compare", after_compare, ["reviews", "respond"])
    g.add_edge("fail", END)
    return g.compile()


GRAPH = build_graph()
