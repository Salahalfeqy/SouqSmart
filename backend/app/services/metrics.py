import threading


class Metrics:
    def __init__(self):
        self._lock = threading.Lock()
        self.reset()

    def reset(self):
        with getattr(self, "_lock", threading.Lock()):
            self.cached_ms = []
            self.uncached_ms = []
            self.rag_ms = []
            self.llm_ms = []

    def record(self, total_ms, cache_hit, rag_ms=0.0, llm_ms=0.0):
        with self._lock:
            (self.cached_ms if cache_hit else self.uncached_ms).append(total_ms)
            if rag_ms:
                self.rag_ms.append(rag_ms)
            if llm_ms:
                self.llm_ms.append(llm_ms)
            for series in (self.cached_ms, self.uncached_ms, self.rag_ms, self.llm_ms):
                del series[:-2000]

    @staticmethod
    def _avg(values):
        return round(sum(values) / len(values), 2) if values else None

    def snapshot(self):
        with self._lock:
            return {
                "avg_cached_ms": self._avg(self.cached_ms),
                "avg_uncached_ms": self._avg(self.uncached_ms),
                "avg_rag_ms": self._avg(self.rag_ms),
                "avg_llm_ms": self._avg(self.llm_ms),
            }


metrics = Metrics()
