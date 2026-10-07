# Evaluation

Run `python scripts/evaluate.py` (results in `docs/evaluation_results.json`) and `cd backend && python -m pytest tests -q`.

## Best-value accuracy: 10/10

Each of the 10 predefined cases checks that the winner: is in the requested category, is within budget, matches a requested brand, has a verified catalog price, and is aligned with the stated priority (for example camera score at or above the median of eligible products, or a noise-cancelling headphone for an ANC request), and that at least three products were compared.

| # | Request | Winner | Result |
|---|---|---|---|
| 1 | I need a smartphone under 20,000 EGP with a great camera | Redmi Note 14 Pro 5G | PASS |
| 2 | Samsung phone under 30000 for gaming | Samsung Galaxy S24 FE | PASS |
| 3 | best laptop for programming under 50000 | ASUS Vivobook 15 | PASS |
| 4 | gaming laptop under 45000 | Acer Nitro V 15 | PASS |
| 5 | noise cancelling headphones under 5000 EGP | Xiaomi Redmi Buds 6 Pro | PASS |
| 6 | Xiaomi phone under 18000 with a big battery | Redmi Note 14 | PASS |
| 7 | lightweight laptop under 30000 for university | Lenovo IdeaPad Slim 3 15 | PASS |
| 8 | Sony or JBL headphones under 6000 with good sound | JBL Tune 770NC | PASS |
| 9 | عاوز موبايل للتصوير في حدود 25 ألف جنيه | Xiaomi 14T | PASS |
| 10 | phone under 10000 | Redmi Note 14 | PASS |

Note: this measures constraint satisfaction and priority alignment against the catalog, not agreement with human shoppers. A human-labelled ground truth would be a stronger test.

## Performance (50 requests: 10 cases x 5 repeats, Redis cache)

| Metric | Value |
|---|---|
| Cache hit rate | 80.0% |
| Avg uncached response | 34.24 ms |
| Avg cached response | 17.97 ms |
| Incorrect price claims | 0 (asserted in tests) |

Cached responses are far below the 1 second target. The uncached path is also fast because the sample catalog has 46 products and a local embedder; with a remote embedding model or LLM the uncached path will be slower and the cache benefit larger.
