WEIGHTS = {"price": 0.30, "performance": 0.25, "specs": 0.20, "preferences": 0.15, "reviews": 0.10}

PRIORITY_ALIASES = {
    "programming": "performance",
    "cpu": "performance",
    "ram": "performance",
    "speed": "performance",
    "work": "performance",
    "sound": "sound",
    "audio": "sound",
    "noise": "anc",
}


def clamp(x, lo=0.0, hi=100.0):
    return max(lo, min(hi, x))


def ratio(value, full):
    try:
        return clamp(float(value) / full * 100)
    except (TypeError, ValueError, ZeroDivisionError):
        return 0.0


def canonical_priority(name):
    name = (name or "").strip().lower()
    return PRIORITY_ALIASES.get(name, name)


def metric_for(product, priority):
    specs, cat = product["specs"], product["category"]
    if priority == "performance":
        return float(specs.get("performance_score", 50))
    if cat == "smartphone":
        if priority == "camera":
            return float(specs.get("camera_score", 50))
        if priority == "gaming":
            return float(specs.get("gaming_score", 50))
        if priority == "battery":
            return ratio(specs.get("battery_mah"), 6500)
        if priority == "display":
            return ratio(specs.get("display_inches"), 6.8)
        if priority == "storage":
            return ratio(specs.get("storage_gb"), 512)
        if priority == "portability":
            return clamp(100 - ratio(specs.get("display_inches"), 6.8) + 40)
    if cat == "laptop":
        if priority == "gaming":
            return float(specs.get("gaming_score", 40))
        if priority == "battery":
            return ratio(specs.get("battery_hours"), 12)
        if priority == "portability":
            return clamp((2.5 - float(specs.get("weight_kg", 2.0))) / 1.4 * 100)
        if priority == "display":
            return ratio(specs.get("display_inches"), 16)
        if priority == "storage":
            return ratio(specs.get("storage_gb"), 1024)
    if cat == "headphones":
        if priority == "sound":
            return float(specs.get("performance_score", 50))
        if priority == "anc":
            return 100.0 if specs.get("anc") else 15.0
        if priority == "battery":
            return ratio(specs.get("battery_hours"), 60)
        if priority == "portability":
            return 90.0 if specs.get("type") == "TWS" else 45.0
    return None


def specs_score(product):
    s, cat = product["specs"], product["category"]
    if cat == "smartphone":
        parts = [ratio(s.get("ram_gb"), 12), ratio(s.get("storage_gb"), 512), ratio(s.get("battery_mah"), 6500), ratio(s.get("display_inches"), 6.8)]
    elif cat == "laptop":
        dedicated = 100 if "RTX" in str(s.get("gpu", "")) or "GTX" in str(s.get("gpu", "")) else 40
        parts = [ratio(s.get("ram_gb"), 16), ratio(s.get("storage_gb"), 512), ratio(s.get("battery_hours"), 12), dedicated]
    else:
        parts = [ratio(s.get("battery_hours"), 60), 100.0 if s.get("anc") else 30.0, ratio(s.get("driver_mm"), 40), 80.0]
    return sum(parts) / len(parts)


def feature_match(product, feature):
    feature = feature.lower().strip()
    specs = product["specs"]
    if feature in {"anc", "noise cancelling", "noise-cancelling"}:
        return bool(specs.get("anc"))
    if feature in {"gpu", "dedicated gpu"}:
        return "RTX" in str(specs.get("gpu", "")) or "GTX" in str(specs.get("gpu", ""))
    haystack = " ".join([product["name"], product["description"]] + [f"{k} {v}" for k, v in specs.items()]).lower()
    return feature in haystack


class ScoringService:
    def __init__(self, weights=None):
        self.weights = weights or WEIGHTS

    def performance_score(self, product, priorities):
        metrics = [m for m in (metric_for(product, canonical_priority(p)) for p in priorities) if m is not None]
        if not metrics:
            return float(product["specs"].get("performance_score", 50))
        base = sum(metrics) / len(metrics)
        return clamp(0.8 * base + 0.2 * float(product["specs"].get("performance_score", base)))

    def preference_score(self, product, prefs):
        parts = []
        brands = [b.lower() for b in prefs.get("preferred_brands") or []]
        if brands:
            parts.append(100.0 if product["brand"].lower() in brands else 0.0)
        budget = prefs.get("budget")
        if budget and product["price"] is not None:
            parts.append(100.0 if product["price"] <= budget else 0.0)
        must = prefs.get("must_have_features") or []
        if must:
            parts.append(sum(feature_match(product, f) for f in must) / len(must) * 100)
        return sum(parts) / len(parts) if parts else 50.0

    def review_score(self, product):
        rating = product["rating"]
        avg = product.get("review_avg")
        blended = rating if avg is None else 0.5 * rating + 0.5 * avg
        return clamp(blended / 5 * 100)

    def score(self, products, prefs=None):
        prefs = prefs or {}
        priorities = prefs.get("priority_features") or []
        priced = [p for p in products if p["price"] is not None]
        lo = min((p["price"] for p in priced), default=0)
        hi = max((p["price"] for p in priced), default=0)
        perf = {p["id"]: self.performance_score(p, priorities) for p in priced}
        ratios = {p["id"]: perf[p["id"]] ** 2 / p["price"] for p in priced}
        top_ratio = max(ratios.values(), default=0) or 1.0
        results = []
        for p in products:
            if p["price"] is None:
                results.append({**p, "value_score": None, "score_breakdown": None, "scored": False})
                continue
            cheap = 100.0 if hi == lo else (hi - p["price"]) / (hi - lo) * 100
            value_ratio = ratios[p["id"]] / top_ratio * 100
            price_component = 0.15 * cheap + 0.85 * value_ratio
            breakdown = {
                "price": round(price_component, 1),
                "performance": round(perf[p["id"]], 1),
                "specs": round(specs_score(p), 1),
                "preferences": round(self.preference_score(p, prefs), 1),
                "reviews": round(self.review_score(p), 1),
            }
            total = sum(breakdown[k] * w for k, w in self.weights.items())
            results.append({**p, "value_score": round(total, 1), "score_breakdown": breakdown, "scored": True})
        results.sort(key=lambda r: (r["value_score"] is None, -(r["value_score"] or 0)))
        return results
