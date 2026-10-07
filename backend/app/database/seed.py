import json

from sqlalchemy import func, select

from app.config import settings
from app.database.database import SessionLocal, init_db
from app.database.models import Product, ProductSpecification, Review


def seed(force: bool = False) -> int:
    init_db()
    with SessionLocal() as db:
        existing = db.scalar(select(func.count(Product.id)))
        if existing and not force:
            return existing
        if existing:
            db.query(Review).delete()
            db.query(ProductSpecification).delete()
            db.query(Product).delete()
            db.commit()
        products = json.loads(settings.products_file.read_text(encoding="utf-8"))
        reviews = json.loads(settings.reviews_file.read_text(encoding="utf-8"))
        for p in products:
            specs = p.pop("specs")
            product = Product(**p)
            product.specs = [ProductSpecification(key=k, value=json.dumps(v)) for k, v in specs.items()]
            db.add(product)
        db.flush()
        for r in reviews:
            db.add(Review(id=r["id"], product_id=r["product_id"], review_text=r["review_text"], rating=r["rating"], source=r["source"]))
        db.commit()
        return len(products)


if __name__ == "__main__":
    print(seed(force=True), "products seeded")
