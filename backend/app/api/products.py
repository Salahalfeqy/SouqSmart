from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import db_session
from app.schemas.schemas import CompareRequest, ProductOut, SearchRequest
from app.services.comparison_service import ComparisonService
from app.services.preference_service import PreferenceService
from app.services.product_service import ProductService
from app.database.repositories import HistoryRepository, UserRepository

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductOut])
def list_products(
    category: str | None = None,
    brand: str | None = None,
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    available_only: bool = False,
    limit: int = Query(default=100, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(db_session),
):
    return ProductService(db).list_products(category, brand, min_price, max_price, available_only, limit, offset)


@router.post("/search", response_model=list[ProductOut])
def search_products(body: SearchRequest, db: Session = Depends(db_session)):
    if body.min_price is not None and body.max_price is not None and body.min_price > body.max_price:
        raise HTTPException(status_code=422, detail="min_price must not exceed max_price")
    return ProductService(db).search(body.query, body.category, body.brands, body.min_price, body.max_price, body.available_only, body.limit)


@router.post("/compare")
def compare_products(body: CompareRequest, db: Session = Depends(db_session)):
    prefs = {"budget": body.budget, "priority_features": body.priority_features, "preferred_brands": body.preferred_brands}
    if body.session_id:
        stored = PreferenceService(db).get(body.session_id)
        prefs = {**stored, **{k: v for k, v in prefs.items() if v}}
    result = ComparisonService(db).compare(body.product_ids, prefs)
    if not result["products"]:
        raise HTTPException(status_code=404, detail="No matching products found")
    if body.session_id:
        user = UserRepository(db).get_or_create(body.session_id)
        HistoryRepository(db).add_comparison(user.id, [p["id"] for p in result["products"]], result["winner_id"])
    return result


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(db_session)):
    product = ProductService(db).get(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
