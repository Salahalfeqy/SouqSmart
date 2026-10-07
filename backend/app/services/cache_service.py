import hashlib
import json
import threading
import time

from app.config import settings

try:
    import redis
except ImportError:
    redis = None


class CacheService:
    def __init__(self, url: str | None = None, ttl: int | None = None):
        self.ttl = ttl if ttl is not None else settings.cache_ttl_seconds
        self.url = url or settings.redis_url
        self._memory: dict[str, tuple[float, str]] = {}
        self._counters = {"hits": 0, "misses": 0}
        self._lock = threading.Lock()
        self._client = None
        self._connect()

    def _connect(self):
        if redis is None or not self.url:
            return
        try:
            client = redis.Redis.from_url(self.url, socket_connect_timeout=0.5, socket_timeout=0.5, decode_responses=True)
            client.ping()
            self._client = client
        except Exception:
            self._client = None

    @property
    def backend(self) -> str:
        return "redis" if self._client is not None else "memory"

    @staticmethod
    def make_key(namespace: str, payload: dict) -> str:
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()[:32]
        return f"souqsmart:{namespace}:{digest}"

    def get(self, key: str):
        value = None
        if self._client is not None:
            try:
                raw = self._client.get(key)
                value = json.loads(raw) if raw else None
            except Exception:
                self._client = None
        if value is None and self._client is None:
            with self._lock:
                entry = self._memory.get(key)
                if entry and entry[0] > time.time():
                    value = json.loads(entry[1])
                elif entry:
                    self._memory.pop(key, None)
        with self._lock:
            self._counters["hits" if value is not None else "misses"] += 1
        return value

    def set(self, key: str, value, ttl: int | None = None):
        ttl = ttl if ttl is not None else self.ttl
        raw = json.dumps(value, ensure_ascii=False, default=str)
        if self._client is not None:
            try:
                self._client.setex(key, ttl, raw)
                return
            except Exception:
                self._client = None
        with self._lock:
            self._memory[key] = (time.time() + ttl, raw)

    def clear(self):
        if self._client is not None:
            try:
                for key in self._client.scan_iter("souqsmart:*"):
                    self._client.delete(key)
            except Exception:
                self._client = None
        with self._lock:
            self._memory.clear()
            self._counters = {"hits": 0, "misses": 0}

    def stats(self) -> dict:
        with self._lock:
            hits, misses = self._counters["hits"], self._counters["misses"]
        total = hits + misses
        return {"backend": self.backend, "ttl_seconds": self.ttl, "hits": hits, "misses": misses, "total": total,
                "hit_rate": round(hits / total * 100, 2) if total else 0.0}


_cache: CacheService | None = None


def get_cache() -> CacheService:
    global _cache
    if _cache is None:
        _cache = CacheService()
    return _cache
