import statistics
import time

from sqlalchemy.orm import Session

from app.database.repositories import HistoryRepository, UserRepository
from app.rag import retriever
from app.rag.retriever import RAGError
from app.services.comparison_service import ComparisonService
from app.services.preference_service import PreferenceService
from app.services.product_service import ProductService, normalize_category
from app.services.scoring_service import ScoringService

CATEGORY_SHARE_FLOOR = 0.15


class AgentTools:
    def __init__(self, db: Session):
        self.db = db
        self.products = ProductService(db)
        self.scorer = ScoringService()
        self.comparer = ComparisonService(db, self.scorer)
        self.preferences = PreferenceService(db)
        self.users = UserRepository(db)
        self.history = HistoryRepository(db)
        self.timings = {"rag_ms": 0.0}

    def search_products(self, query=None, category=None, brand=None, min_price=None, max_price=None, available_only=True, limit=50):
        brands = [brand] if isinstance(brand, str) else (brand or [])
        return self.products.search(query=query, category=category, brands=brands, min_price=min_price, max_price=max_price, available_only=available_only, limit=limit)

    def semantic_search(self, query, category=None, brands=None, max_price=None, k=10):
        started = time.perf_counter()
        try:
            hits = retriever.semantic_product_search(query, category=normalize_category(category), brands=brands, max_price=max_price, available_only=True, k=k)
        except RAGError:
            return []
        finally:
            self.timings["rag_ms"] += (time.perf_counter() - started) * 1000
        return self.products.get_many([h["product_id"] for h in hits])

    def filter_products(self, products, category=None, brands=None, min_price=None, max_price=None, available_only=True, require_price=True):
        return self.products.filter_products(products, category, brands, min_price, max_price, available_only, require_price)

    def calculate_value_score(self, products, prefs):
        return self.scorer.score(products, prefs)

    def compare_products(self, product_ids, prefs, min_items=3):
        return self.comparer.compare(product_ids, prefs, min_items)

    @staticmethod
    def _prefer_language(reviews, lang, k):
        def is_ar(text):
            return any("\u0600" <= c <= "\u06ff" for c in text)

        ordered = sorted(reviews, key=lambda r: 0 if is_ar(r["text"]) == (lang == "ar") else 1)
        return ordered[:k]

    def retrieve_reviews(self, query, product_ids, k_per_product=2, lang="en"):
        started = time.perf_counter()
        degraded = False
        try:
            found = retriever.retrieve_reviews(query, product_ids, k_per_product * 3)
            found = {pid: self._prefer_language(items, lang, k_per_product) for pid, items in found.items()}
        except RAGError:
            degraded = True
            found = {}
            for pid in product_ids:
                product = self.products.repo.get(pid)
                reviews = sorted(product.reviews, key=lambda r: -r.rating) if product else []
                items = [{"text": r.review_text, "rating": r.rating, "source": r.source, "score": 0.0} for r in reviews]
                found[pid] = self._prefer_language(items, lang, k_per_product)
        finally:
            self.timings["rag_ms"] += (time.perf_counter() - started) * 1000
        return found, degraded

    def save_preferences(self, session_id, data):
        return self.preferences.save(session_id, data)

    def get_user_preferences(self, session_id):
        return self.preferences.get(session_id)

    def build_shopping_list(self, categories, total_budget, prefs):
        categories = [normalize_category(c) for c in categories]
        catalog = {c: [p for p in self.products.search(category=c, available_only=True, limit=200) if p["price"] is not None] for c in categories}
        catalog = {c: v for c, v in catalog.items() if v}
        if not catalog:
            return {"items": [], "total": 0, "remaining": total_budget, "missing": categories}
        medians = {c: statistics.median(p["price"] for p in v) for c, v in catalog.items()}
        total_median = sum(medians.values())
        items, missing = [], [c for c in categories if c not in catalog]
        for c, pool in catalog.items():
            cap = None
            if total_budget:
                cap = total_budget * max(medians[c] / total_median, CATEGORY_SHARE_FLOOR)
            candidates = [p for p in pool if cap is None or p["price"] <= cap]
            category_prefs = {**prefs, "budget": cap}
            if not candidates:
                cheapest = min(pool, key=lambda p: p["price"])
                items.append({"category": c, "product": None, "cheapest_price": cheapest["price"], "cheapest_name": cheapest["name"], "allocation": cap})
                continue
            ranked = self.scorer.score(candidates, category_prefs)
            best = next(r for r in ranked if r["scored"])
            items.append({"category": c, "product": best, "allocation": cap})
        total = sum(i["product"]["price"] for i in items if i["product"])
        if total_budget:
            for _ in range(3):
                leftover = total_budget - total
                upgraded = False
                for it in items:
                    if not it["product"]:
                        continue
                    pool = [p for p in catalog[it["category"]] if it["product"]["price"] < p["price"] <= it["product"]["price"] + leftover]
                    if not pool:
                        continue
                    ranked = self.scorer.score(pool + [it["product"]], {**prefs, "budget": it["product"]["price"] + leftover})
                    top = next(r for r in ranked if r["scored"])
                    if top["id"] != it["product"]["id"]:
                        total += top["price"] - it["product"]["price"]
                        it["product"] = top
                        upgraded = True
                        break
                if not upgraded:
                    break
        return {"items": items, "total": total, "remaining": (total_budget - total) if total_budget else None, "missing": missing, "budget": total_budget}


TOOL_NAMES = [
    "search_products", "filter_products", "compare_products", "calculate_value_score",
    "retrieve_reviews", "save_preferences", "get_user_preferences", "build_shopping_list",
]
