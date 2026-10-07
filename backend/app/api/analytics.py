from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import cache_service, db_session
from app.services.analytics_service import AnalyticsService
from app.services.cache_service import CacheService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("")
def analytics(db: Session = Depends(db_session)):
    return AnalyticsService(db).summary()


@router.post("/cache/clear")
def clear_cache(cache: CacheService = Depends(cache_service)):
    cache.clear()
    return {"cleared": True}
