import hashlib
import math
import re

from app.config import settings

TOKEN_RE = re.compile(r"[a-z0-9؀-ۿ]+")


def normalize_text(text: str) -> str:
    text = (text or "").lower()
    text = re.sub(r"[ً-ٟـ]", "", text)
    return text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ة", "ه").replace("ى", "ي")


def features(text: str):
    tokens = TOKEN_RE.findall(normalize_text(text))
    for tok in tokens:
        yield tok, 1.0
        padded = f"#{tok}#"
        if len(padded) > 3:
            for i in range(len(padded) - 2):
                yield padded[i: i + 3], 0.35
    for a, b in zip(tokens, tokens[1:]):
        yield f"{a}_{b}", 0.6


class HashingEmbedder:
    def __init__(self, dim: int | None = None):
        self.dim = dim or settings.embedding_dim

    def embed(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        for feat, weight in features(text):
            digest = hashlib.md5(feat.encode("utf-8")).digest()
            idx = int.from_bytes(digest[:4], "little") % self.dim
            sign = 1.0 if digest[4] & 1 else -1.0
            vec[idx] += sign * weight
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(t) for t in texts]


_embedder: HashingEmbedder | None = None


def get_embedder() -> HashingEmbedder:
    global _embedder
    if _embedder is None:
        _embedder = HashingEmbedder()
    return _embedder
