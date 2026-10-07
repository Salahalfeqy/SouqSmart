from collections import Counter

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import ComparisonHistory, Product, SearchHistory
from app.services.cache_service import get_cache
from app.services.metrics import metrics


def avg(values):
    return round(sum(values) / len(values), 4) if values else None


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def summary(self) -> dict:
        searches = list(self.db.scalars(select(SearchHistory)).all())
        comparisons = list(self.db.scalars(select(ComparisonHistory)).all())
        names = {pid: (name, brand) for pid, name, brand in self.db.execute(select(Product.id, Product.name, Product.brand))}

        categories = Counter(s.category for s in searches if s.category)
        brands = Counter(s.brand for s in searches if s.brand)
        compared = Counter()
        brand_compared = Counter()
        for c in comparisons:
            for pid in c.product_ids:
                if pid in names:
                    compared[names[pid][0]] += 1
                    brand_compared[names[pid][1]] += 1
        winners = Counter(names[c.selected_product_id][0] for c in comparisons if c.selected_product_id in names)

        hits = [s for s in searches if s.cache_hit]
        misses = [s for s in searches if not s.cache_hit]
        total = len(searches)
        popular_brand = (brands + brand_compared).most_common(1)
        cache_live = get_cache().stats()
        daily = Counter(s.created_at.date().isoformat() for s in searches)
        recent = sorted(searches, key=lambda s: s.created_at)[-50:]

        return {
            "total_searches": total,
            "total_comparisons": len(comparisons),
            "cache": {
                "hits": len(hits),
                "misses": len(misses),
                "total_requests": total,
                "hit_rate": round(len(hits) / total * 100, 2) if total else 0.0,
                "avg_cached_response_s": avg([s.response_time for s in hits]),
                "avg_uncached_response_s": avg([s.response_time for s in misses]),
                "backend": cache_live["backend"],
                "ttl_seconds": cache_live["ttl_seconds"],
            },
            "avg_response_time_s": avg([s.response_time for s in searches]),
            "popular_category": categories.most_common(1)[0][0] if categories else None,
            "popular_brand": popular_brand[0][0] if popular_brand else None,
            "categories": dict(categories),
            "brands": dict(brands + brand_compared),
            "most_compared_products": dict(compared.most_common(10)),
            "top_recommended_products": dict(winners.most_common(10)),
            "searches_per_day": dict(sorted(daily.items())),
            "response_times": [{"id": s.id, "seconds": s.response_time, "cache_hit": s.cache_hit} for s in recent],
            "component_latency_ms": metrics.snapshot(),
        }
