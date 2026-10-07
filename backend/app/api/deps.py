from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services.cache_service import CacheService, get_cache


def db_session(db: Session = Depends(get_db)) -> Session:
    return db


def cache_service() -> CacheService:
    return get_cache()
