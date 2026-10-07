from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Product


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, product_id: int):
        return self.db.get(Product, product_id)

    def get_many(self, ids: list[int]):
        if not ids:
            return []
        rows = self.db.scalars(select(Product).where(Product.id.in_(ids))).all()
        order = {pid: i for i, pid in enumerate(ids)}
        return sorted(rows, key=lambda p: order[p.id])

    def query(self, category=None, brands=None, min_price=None, max_price=None, in_stock_only=False, require_price=False):
        stmt = select(Product)
        if category:
            stmt = stmt.where(Product.category == category)
        if brands:
            stmt = stmt.where(Product.brand.in_(brands))
        if min_price is not None:
            stmt = stmt.where(Product.price >= min_price)
        if max_price is not None:
            stmt = stmt.where(Product.price <= max_price)
        if in_stock_only:
            stmt = stmt.where(Product.stock > 0)
        if require_price or min_price is not None or max_price is not None:
            stmt = stmt.where(Product.price.is_not(None))
        return list(self.db.scalars(stmt.order_by(Product.id)).all())

    def all(self):
        return list(self.db.scalars(select(Product).order_by(Product.id)).all())

    def brands(self):
        return sorted({b for (b,) in self.db.execute(select(Product.brand).distinct())})
