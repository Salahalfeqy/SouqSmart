import json
import os
import sys
import tempfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
tmp = tempfile.mkdtemp(prefix="souqsmart_eval_")
os.environ["DATABASE_URL"] = f"sqlite:///{tmp}/eval.db"
os.environ["CHROMA_PATH"] = f"{tmp}/chroma"
os.environ["REDIS_URL"] = os.getenv("EVAL_REDIS_URL", "")
sys.path.insert(0, str(root / "backend"))
sys.path.insert(0, str(root / "backend" / "tests"))

from app.agents.runner import handle_chat
from app.database.database import SessionLocal
from app.database.seed import seed
from app.rag.ingestion import ingest
from app.services.cache_service import CacheService
from test_cases import CASES, evaluate_case

seed(force=True)
with SessionLocal() as db:
    ingest(db, rebuild=True)
    outcomes = [evaluate_case(db, c) for c in CASES]

    cache = CacheService(url=os.environ["REDIS_URL"])
    cache.clear()
    cold, warm = [], []
    for case in CASES:
        for i in range(5):
            r = handle_chat(db, f"bench-{case['id']}-{i}", case["message"], cache)
            (warm if r["cache_hit"] else cold).append(r["response_time"] * 1000)

passed = sum(o["passed"] for o in outcomes)
summary = {
    "cases": outcomes,
    "best_value_accuracy": f"{passed}/{len(outcomes)}",
    "avg_uncached_ms": round(sum(cold) / len(cold), 2),
    "avg_cached_ms": round(sum(warm) / len(warm), 2),
    "cache_hit_rate_pct": round(len(warm) / (len(warm) + len(cold)) * 100, 1),
    "cache_backend": cache.backend,
}
(root / "docs" / "evaluation_results.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps({k: v for k, v in summary.items() if k != "cases"}, indent=2))
for o in outcomes:
    print(o["case"], "PASS" if o["passed"] else "FAIL", o["winner"], [k for k, v in o["checks"].items() if not v])
