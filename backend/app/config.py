import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data"))


class Settings:
    app_name = "SouqSmart"
    api_prefix = "/api/v1"
    database_url = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'souqsmart.db'}")
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    chroma_path = os.getenv("CHROMA_PATH", str(BASE_DIR / "rag" / "vector_store"))
    cache_ttl_seconds = int(os.getenv("CACHE_TTL_SECONDS", "600"))
    llm_api_key = os.getenv("OPENAI_API_KEY", "")
    llm_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    llm_model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    llm_timeout = float(os.getenv("LLM_TIMEOUT", "20"))
    products_file = DATA_DIR / "products" / "products.json"
    reviews_file = DATA_DIR / "reviews" / "reviews.json"
    embedding_dim = 384


settings = Settings()
