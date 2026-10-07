from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import ComparisonHistory, SearchHistory


class HistoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_search(self, user_id, query, category, brand, intent, response_time, cache_hit):
        row = SearchHistory(user_id=user_id, query=query[:500], category=category, brand=brand, intent=intent,
                            response_time=response_time, cache_hit=cache_hit)
        self.db.add(row)
        self.db.commit()
        return row

    def add_comparison(self, user_id, product_ids, selected_product_id):
        row = ComparisonHistory(user_id=user_id, product_ids=list(product_ids), selected_product_id=selected_product_id)
        self.db.add(row)
        self.db.commit()
        return row

    def searches(self):
        return list(self.db.scalars(select(SearchHistory)).all())

    def comparisons(self):
        return list(self.db.scalars(select(ComparisonHistory)).all())
