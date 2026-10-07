from app.agents.runner import handle_chat
from app.services.requirement_service import extract_requirements


def test_extract_budget_variants():
    assert extract_requirements("budget 25,000 EGP").budget == 25000
    assert extract_requirements("What if my budget becomes 30K?").budget == 30000
    assert extract_requirements("في حدود 25 ألف جنيه").budget == 25000
    assert extract_requirements("phone with 16GB ram and 5000mAh battery").budget is None
    r = extract_requirements("between 15000 and 20000")
    assert (r.min_price, r.budget) == (15000, 20000)


def test_extract_arabic_requirements():
    r = extract_requirements("عاوز موبايل سامسونج للتصوير والجيمنج")
    assert r.categories == ["smartphone"] and r.brands == ["Samsung"]
    assert set(r.priorities) == {"camera", "gaming"}
    assert r.language == "ar"


def test_multi_turn_memory(db, cache):
    sid = "memory-1"
    r1 = handle_chat(db, sid, "I need a smartphone for gaming and photography.", cache)
    assert "budget" in r1["reply"].lower()
    r2 = handle_chat(db, sid, "25,000 EGP.", cache)
    assert r2["payload"]["type"] == "recommend"
    r3 = handle_chat(db, sid, "I prefer Samsung or Xiaomi", cache)
    assert all(c["brand"] in {"Samsung", "Xiaomi"} for c in r3["payload"]["cards"])
    assert r3["preferences"]["budget"] == 25000
    r4 = handle_chat(db, sid, "What if my budget becomes 30K?", cache)
    assert r4["preferences"]["budget"] == 30000
    assert r4["preferences"]["preferred_brands"] == ["Samsung", "Xiaomi"]
    assert r4["preferences"]["priority_features"] == ["gaming", "camera"] or set(r4["preferences"]["priority_features"]) == {"gaming", "camera"}
    r5 = handle_chat(db, sid, "Show me the best one", cache)
    assert r5["payload"]["type"] == "recommend"
    assert r5["payload"]["winner_id"] == r4["payload"]["winner_id"]


def test_compare_named_products_at_least_three(db, cache):
    r = handle_chat(db, "cmp-1", "Compare Samsung A56 and Xiaomi 14T", cache)
    assert r["payload"]["type"] == "compare"
    assert len(r["payload"]["cards"]) >= 3
    names = {c["name"] for c in r["payload"]["cards"]}
    assert "Samsung Galaxy A56 5G" in names and "Xiaomi 14T" in names


def test_missing_price_is_never_invented(db, cache):
    r = handle_chat(db, "price-missing", "Compare Dell XPS 13 and Asus Zenbook 14 and Acer Swift Go", cache)
    dell = next(c for c in r["payload"]["cards"] if "XPS" in c["name"])
    assert dell["price"] is None and dell["value_score"] is None
    assert "verified price" in r["reply"]


def test_out_of_stock_not_recommended(db, cache):
    r = handle_chat(db, "stock-1", "Oppo A3", cache)
    assert r["payload"]["winner_id"] != next(c["id"] for c in r["payload"]["cards"] if c["name"] == "Oppo A3")


def test_no_results_graceful(db, cache):
    r = handle_chat(db, "empty-1", "headphones under 100 EGP", cache)
    assert r["payload"]["cards"] or "couldn't find" in r["reply"] or r["payload"]["notes"]
    assert r["error"] is None


def test_greeting_and_gibberish(db, cache):
    assert handle_chat(db, "hi-1", "hello", cache)["payload"]["type"] == "message"
    assert handle_chat(db, "hi-2", "asdf qwerty", cache)["payload"]["type"] == "message"


def test_arabic_reply(db, cache):
    r = handle_chat(db, "ar-1", "عاوز لابتوب للبرمجة بحدود 40 ألف جنيه", cache)
    assert "جنيه" in r["reply"]
    assert r["payload"]["type"] == "recommend"


def test_shopping_list_total_within_budget(db, cache):
    r = handle_chat(db, "list-1", "I need a phone, headphones and a laptop, budget 90000", cache)
    assert r["payload"]["type"] == "shopping_list"
    assert 0 < r["payload"]["shopping_total"] <= 90000
    assert {c["category"] for c in r["payload"]["cards"]} == {"smartphone", "laptop", "headphones"}


def test_reviews_intent(db, cache):
    r = handle_chat(db, "rev-1", "What do customers think about Samsung A56?", cache)
    assert r["payload"]["type"] == "reviews"
    assert r["payload"]["cards"][0]["reviews"]


def test_rag_failure_falls_back(db, cache, monkeypatch):
    from app.rag import retriever

    def boom(*a, **k):
        raise retriever.RAGError("down")

    monkeypatch.setattr(retriever, "_query", boom)
    r = handle_chat(db, "rag-1", "phone under 20000 for camera", cache)
    assert r["payload"]["type"] == "recommend"
    assert r["payload"]["cards"][0]["reviews"]
    assert any("Review search" in n for n in r["payload"]["notes"])


def test_database_failure_message(db, cache, monkeypatch):
    from sqlalchemy.exc import OperationalError

    from app.agents import tools as tools_pkg

    def boom(self, *a, **k):
        raise OperationalError("select", {}, Exception("db down"))

    monkeypatch.setattr(tools_pkg.AgentTools, "get_user_preferences", boom)
    from app.agents.runner import run_agent

    r = run_agent(db, "db-down", "phone under 20000", cache)
    assert r["error"] == "db"
    assert "database" in r["reply"].lower()
