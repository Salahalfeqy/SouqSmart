import json
import time
from pathlib import Path

import pytest

from app.agents.runner import handle_chat
from app.services.product_service import ProductService

CASES = [
    {"id": 1, "message": "I need a smartphone under 20,000 EGP with a great camera", "category": "smartphone", "budget": 20000, "priority": "camera", "brand": None},
    {"id": 2, "message": "Samsung phone under 30000 for gaming", "category": "smartphone", "budget": 30000, "priority": "gaming", "brand": "Samsung"},
    {"id": 3, "message": "best laptop for programming under 50000", "category": "laptop", "budget": 50000, "priority": "performance", "brand": None},
    {"id": 4, "message": "gaming laptop under 45000", "category": "laptop", "budget": 45000, "priority": "gaming", "brand": None},
    {"id": 5, "message": "noise cancelling headphones under 5000 EGP", "category": "headphones", "budget": 5000, "priority": "anc", "brand": None},
    {"id": 6, "message": "Xiaomi phone under 18000 with a big battery", "category": "smartphone", "budget": 18000, "priority": "battery", "brand": "Xiaomi"},
    {"id": 7, "message": "lightweight laptop under 30000 for university", "category": "laptop", "budget": 30000, "priority": "portability", "brand": None},
    {"id": 8, "message": "Sony or JBL headphones under 6000 with good sound", "category": "headphones", "budget": 6000, "priority": "sound", "brand": "Sony,JBL"},
    {"id": 9, "message": "عاوز موبايل للتصوير في حدود 25 ألف جنيه", "category": "smartphone", "budget": 25000, "priority": "camera", "brand": None},
    {"id": 10, "message": "phone under 10000", "category": "smartphone", "budget": 10000, "priority": None, "brand": None},
]

SPEC_KEY = {"camera": "camera_score", "gaming": "gaming_score", "performance": "performance_score", "sound": "performance_score"}


def evaluate_case(db, case):
    session = f"eval-{case['id']}"
    result = handle_chat(db, session, case["message"], None)
    cards = result["payload"]["cards"]
    winner_id = result["payload"]["winner_id"]
    service = ProductService(db)
    winner = service.get(winner_id) if winner_id else None
    checks = {
        "has_three_products": len(cards) >= 3 or (winner is not None and len(cards) >= 2),
        "winner_in_budget": winner is not None and winner["price"] is not None and winner["price"] <= case["budget"],
        "category_match": winner is not None and winner["category"] == case["category"],
        "brand_match": case["brand"] is None or (winner is not None and winner["brand"] in case["brand"].split(",")),
        "prices_match_catalog": all(c["price"] == service.get(c["id"])["price"] for c in cards),
    }
    if case["priority"] and winner:
        pool = [p for p in service.search(category=case["category"], available_only=True, limit=100) if p["price"] and p["price"] <= case["budget"]]
        if case["brand"]:
            pool = [p for p in pool if p["brand"] in case["brand"].split(",")]
        key = SPEC_KEY.get(case["priority"])
        if key:
            values = sorted(p["specs"].get(key, 0) for p in pool)
            median = values[len(values) // 2]
            checks["priority_aligned"] = winner["specs"].get(key, 0) >= median
        elif case["priority"] == "battery":
            checks["priority_aligned"] = winner["specs"]["battery_mah"] >= 5000
        elif case["priority"] == "anc":
            checks["priority_aligned"] = bool(winner["specs"].get("anc"))
        elif case["priority"] == "portability":
            checks["priority_aligned"] = winner["specs"]["weight_kg"] <= 1.7
    return {"case": case["id"], "message": case["message"], "winner": winner["name"] if winner else None, "checks": checks, "passed": all(checks.values()), "response_time": result["response_time"]}


@pytest.mark.parametrize("case", CASES, ids=[f"case{c['id']}" for c in CASES])
def test_predefined_case(db, case):
    outcome = evaluate_case(db, case)
    assert outcome["passed"], json.dumps(outcome, ensure_ascii=False)


def test_best_value_accuracy_target(db):
    outcomes = [evaluate_case(db, c) for c in CASES]
    assert sum(o["passed"] for o in outcomes) >= 8


def test_price_never_invented(db):
    for case in CASES:
        result = handle_chat(db, f"price-{case['id']}", case["message"], None)
        service = ProductService(db)
        allowed = {int(p["price"]) for p in service.list_products(limit=1000) if p["price"] is not None}
        allowed.add(case["budget"])
        for card in result["payload"]["cards"]:
            assert card["price"] is None or int(card["price"]) in allowed
        import re

        for m in re.findall(r"(\d{1,3}(?:,\d{3})+)\s*(?:EGP|جنيه)", result["reply"]):
            assert int(m.replace(",", "")) in allowed or int(m.replace(",", "")) <= case["budget"]


def test_cache_improves_response_time(db, cache):
    msg = "best phone under 25000 for gaming"
    first = handle_chat(db, "perf-1", msg, cache)
    second = handle_chat(db, "perf-1", msg, cache)
    assert not first["cache_hit"] and second["cache_hit"]
    assert second["response_time"] < 1.0
    assert second["reply"] == first["reply"]


def write_report(path: Path):
    from app.database.database import SessionLocal

    with SessionLocal() as db:
        outcomes = [evaluate_case(db, c) for c in CASES]
    path.write_text(json.dumps(outcomes, indent=2, ensure_ascii=False), encoding="utf-8")
    return outcomes
