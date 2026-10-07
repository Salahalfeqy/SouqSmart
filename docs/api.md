# API (v1)

Base path `/api/v1`. Interactive docs at `/docs`. Health at `/health`.

| Method | Path | Purpose |
|---|---|---|
| GET | `/products` | List with `category`, `brand`, `min_price`, `max_price`, `available_only`, `limit`, `offset` |
| GET | `/products/{id}` | One product with specs (404 if missing) |
| POST | `/products/search` | Body: `query`, `category`, `brands`, `min_price`, `max_price`, `available_only`, `limit` |
| POST | `/products/compare` | Body: `product_ids` (1-6), optional `session_id`, `budget`, `priority_features`, `preferred_brands`. Pads to 3 products |
| POST | `/chat` | Body: `session_id`, `message`. Returns `reply`, `payload` (cards, winner), `preferences`, `cache_hit`, `response_time`, `trace` |
| GET | `/preferences/{session_id}` | Stored preferences |
| POST | `/preferences` | Save/merge preferences |
| DELETE | `/preferences/{session_id}` | Clear preferences |
| GET | `/sessions` | Conversation list for the history sidebar |
| GET | `/sessions/{session_id}/messages` | Full conversation |
| GET | `/analytics` | KPIs, chart data, cache metrics |
| POST | `/analytics/cache/clear` | Clear the cache |

Example:

```bash
curl -X POST localhost:8000/api/v1/chat -H 'content-type: application/json' \
  -d '{"session_id":"abc123","message":"Best phone under 25000 for gaming?"}'
```
