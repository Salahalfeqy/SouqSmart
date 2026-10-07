import os
import sys
import tempfile
from pathlib import Path

_tmp = tempfile.mkdtemp(prefix="souqsmart_test_")
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp}/test.db"
os.environ["CHROMA_PATH"] = f"{_tmp}/chroma"
os.environ["REDIS_URL"] = ""
os.environ["OPENAI_API_KEY"] = ""
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient

from app.database.database import SessionLocal
from app.database.seed import seed
from app.main import app
from app.rag.ingestion import ingest
from app.services.cache_service import CacheService, get_cache


@pytest.fixture(scope="session", autouse=True)
def bootstrap():
    seed(force=True)
    with SessionLocal() as db:
        ingest(db, rebuild=True)
    yield


@pytest.fixture()
def db():
    with SessionLocal() as session:
        yield session


@pytest.fixture()
def cache():
    c = CacheService(url="")
    return c


@pytest.fixture()
def client():
    get_cache().clear()
    with TestClient(app) as c:
        yield c
