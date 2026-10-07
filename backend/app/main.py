import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api import analytics, chat, products, users
from app.config import settings
from app.database.database import SessionLocal
from app.database.seed import seed
from app.rag.ingestion import ensure_ingested
from app.services.cache_service import get_cache

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("souqsmart")


@asynccontextmanager
async def lifespan(app: FastAPI):
    seed()
    try:
        with SessionLocal() as db:
            logger.info("rag ingest: %s", ensure_ingested(db))
    except Exception:
        logger.exception("RAG ingestion failed, reviews will fall back to the relational database")
    logger.info("cache backend: %s", get_cache().backend)
    yield


app = FastAPI(title="SouqSmart API", version="1.0.0", lifespan=lifespan)

for router in (products.router, chat.router, users.router, analytics.router):
    app.include_router(router, prefix=settings.api_prefix)


@app.get("/health")
def health():
    cache = get_cache()
    return {"status": "ok", "cache_backend": cache.backend, "llm_enabled": bool(settings.llm_api_key)}


@app.exception_handler(Exception)
async def unhandled(request: Request, exc: Exception):
    logger.exception("unhandled error on %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
