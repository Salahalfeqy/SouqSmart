from sqlalchemy.orm import Session

from app.services.product_service import ProductService
from app.services.scoring_service import ScoringService

SPEC_LABELS = {
    "smartphone": ["chipset", "ram_gb", "storage_gb", "battery_mah", "main_camera_mp", "display_inches"],
    "laptop": ["cpu", "ram_gb", "storage_gb", "gpu", "display_inches", "weight_kg", "battery_hours"],
    "headphones": ["type", "anc", "battery_hours", "driver_mm", "bluetooth"],
}


class ComparisonService:
    def __init__(self, db: Session, scorer: ScoringService | None = None):
        self.db = db
        self.products = ProductService(db)
        self.scorer = scorer or ScoringService()

    def compare(self, product_ids: list[int], prefs: dict | None = None, min_items: int = 3):
        prefs = prefs or {}
        items = self.products.get_many(list(dict.fromkeys(product_ids)))
        notes = []
        if not items:
            return {"products": [], "winner_id": None, "notes": ["no_products"], "spec_keys": []}
        category = items[0]["category"]
        items = [p for p in items if p["category"] == category]
        if len(items) < min_items:
            have = {p["id"] for p in items}
            pool = [p for p in self.products.search(category=category, limit=100) if p["id"] not in have and p["price"] is not None and p["available"]]
            budget = prefs.get("budget")
            over_budget = False
            if budget:
                within = [p for p in pool if p["price"] <= budget]
                if within:
                    pool = within
                else:
                    pool = sorted(pool, key=lambda p: p["price"])
                    over_budget = True
            ranked = self.scorer.score(items + pool, prefs)
            extras = [r for r in ranked if r["id"] not in have and r["scored"]]
            added = extras[: min_items - len(items)]
            if added:
                notes.append("alternatives_over_budget" if over_budget else "added_alternatives")
            items = items + [{k: v for k, v in a.items() if k not in {"value_score", "score_breakdown", "scored"}} for a in added]
        scored = self.scorer.score(items, prefs)
        budget = prefs.get("budget")
        eligible = [p for p in scored if p["scored"] and p["available"] and (not budget or p["price"] <= budget)]
        winner = (eligible or [p for p in scored if p["scored"] and p["available"]] or [p for p in scored if p["scored"]] or [None])[0]
        for p in scored:
            if not p["price_verified"]:
                notes.append(f"price_unavailable:{p['id']}")
            if not p["available"]:
                notes.append(f"out_of_stock:{p['id']}")
        return {
            "category": category,
            "products": scored,
            "winner_id": winner["id"] if winner else None,
            "notes": notes,
            "spec_keys": SPEC_LABELS.get(category, []),
        }
