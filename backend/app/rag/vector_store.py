import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import settings

PRODUCTS = "souqsmart_products"
REVIEWS = "souqsmart_reviews"

_client = None


def get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=settings.chroma_path, settings=ChromaSettings(anonymized_telemetry=False))
    return _client


def get_collection(name: str):
    return get_client().get_or_create_collection(name=name, metadata={"hnsw:space": "cosine"}, embedding_function=None)


def reset_collections():
    client = get_client()
    for name in (PRODUCTS, REVIEWS):
        try:
            client.delete_collection(name)
        except Exception:
            pass
