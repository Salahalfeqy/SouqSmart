import json
import re

from sqlalchemy.orm import Session

from app.database.repositories import ProductRepository

CATEGORY_ALIASES = {
    "smartphone": "smartphone",
    "smartphones": "smartphone",
    "phone": "smartphone",
    "phones": "smartphone",
    "mobile": "smartphone",
    "laptop": "laptop",
    "laptops": "laptop",
    "notebook": "laptop",
    "headphones": "headphones",
    "headphone": "headphones",
    "earbuds": "headphones",
    "headset": "headphones",
}

TOKEN_RE = re.compile(r"[a-z0-9؀-ۿ\+]+")


def normalize_category(value):
    if not value:
        return None
    return CATEGORY_ALIASES.get(value.strip().lower(), value.strip().lower())


def tokenize(text: str):
    return TOKEN_RE.findall((text or "").lower())


def decode_spec(value: str):
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        return value


def product_to_dict(product) -> dict:
    specs = {s.key: decode_spec(s.value) for s in product.specs}
    ratings = [r.rating for r in product.reviews]
    return {
        "id": product.id,
        "name": product.name,
        "brand": product.brand,
        "category": product.category,
        "price": product.price,
        "old_price": product.old_price,
        "price_verified": product.price is not None,
        "description": product.description,
        "rating": product.rating,
        "stock": product.stock,
        "available": product.stock > 0,
        "url": product.url,
        "image_url": product.image_url,
        "specs": specs,
        "review_count": len(ratings),
        "review_avg": round(sum(ratings) / len(ratings), 2) if ratings else None,
    }


class ProductService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ProductRepository(db)

    def get(self, product_id: int):
        product = self.repo.get(product_id)
        return product_to_dict(product) if product else None

    def get_many(self, ids: list[int]):
        return [product_to_dict(p) for p in self.repo.get_many(ids)]

    def brands(self):
        return self.repo.brands()

    def list_products(self, category=None, brand=None, min_price=None, max_price=None, available_only=False, limit=100, offset=0):
        brands = [brand] if isinstance(brand, str) and brand else brand
        rows = self.repo.query(normalize_category(category), brands, min_price, max_price, available_only)
        return [product_to_dict(p) for p in rows][offset: offset + limit]

    def search(self, query=None, category=None, brands=None, min_price=None, max_price=None, available_only=False, limit=20):
        category = normalize_category(category)
        brands = [b for b in (brands or []) if b]
        rows = [product_to_dict(p) for p in self.repo.query(category, None, min_price, max_price, available_only)]
        wanted = {b.lower() for b in brands}
        if wanted:
            rows = [p for p in rows if p["brand"].lower() in wanted]
        tokens = [t for t in tokenize(query) if len(t) > 1] if query else []
        if tokens:
            scored = []
            for p in rows:
                haystack = set(tokenize(" ".join([p["name"], p["brand"], p["category"], p["description"], " ".join(f"{k} {v}" for k, v in p["specs"].items())])))
                name_tokens = set(tokenize(p["name"]))
                hits = sum(1 for t in tokens if t in haystack)
                name_hits = sum(1 for t in tokens if t in name_tokens)
                scored.append((name_hits * 3 + hits, p))
            matched = [(s, p) for s, p in scored if s > 0]
            if matched:
                rows = [p for _, p in sorted(matched, key=lambda x: (-x[0], -x[1]["rating"]))]
            elif not (category or wanted):
                rows = []
        else:
            rows.sort(key=lambda p: -p["rating"])
        return rows[:limit]

    @staticmethod
    def filter_products(products, category=None, brands=None, min_price=None, max_price=None, available_only=False, require_price=False):
        category = normalize_category(category)
        wanted = {b.lower() for b in (brands or [])}
        out = []
        for p in products:
            if category and p["category"] != category:
                continue
            if wanted and p["brand"].lower() not in wanted:
                continue
            if available_only and not p["available"]:
                continue
            if (require_price or min_price is not None or max_price is not None) and p["price"] is None:
                continue
            if min_price is not None and p["price"] < min_price:
                continue
            if max_price is not None and p["price"] > max_price:
                continue
            out.append(p)
        return out

    GENERIC = {"galaxy", "5g", "gen", "ultra", "slim"}
    OPTIONAL = {"oled", "gaming"}
    LAPTOP_SIZES = {"13", "14", "15"}

    @classmethod
    def required_tokens(cls, product):
        distinct = [t for t in tokenize(product.name) if t != product.brand.lower() and t not in cls.GENERIC]
        trimmed = [t for t in distinct if not (len(t) >= 6 and re.search(r"\d", t) and re.search(r"[a-z]", t)) and not (t.isdigit() and len(t) >= 4)]
        trimmed = [t for t in trimmed if t not in cls.OPTIONAL and not (t.isdigit() and len(t) == 1)]
        if product.category == "laptop":
            trimmed = [t for t in trimmed if t not in cls.LAPTOP_SIZES]
        return trimmed or distinct

    def find_by_names(self, text: str):
        text_tokens = set(tokenize(text))
        matched = []
        for p in self.repo.all():
            required = self.required_tokens(p)
            if required and all(t in text_tokens for t in required):
                matched.append(p)
        names = [p.name.lower() for p in matched]
        result = []
        for p in matched:
            req = set(self.required_tokens(p))
            superseded = any(q.id != p.id and req < set(self.required_tokens(q)) for q in matched)
            if not superseded:
                result.append(p)
        return [product_to_dict(p) for p in result]
