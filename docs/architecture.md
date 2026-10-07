# Architecture

```
Streamlit UI -> FastAPI /api/v1 -> LangGraph agent -> tools -> PostgreSQL / Chroma
                                        |                      
                                      Redis cache (TTL)  ->  analytics from SearchHistory
```

## Agent graph

```
load_preferences -> understand -> remember -> gate
   gate -> simple_reply (greeting, clarify, ask category/budget, reset)  -> END
   gate -> check_cache
      hit  -> done
      miss -> by intent:
        recommend      : search -> score_rank -> compare -> reviews -> respond -> store_cache
        compare        : resolve -> compare -> reviews -> respond -> store_cache
        reviews        : resolve -> reviews -> respond -> store_cache
        shopping_list  : build_list -> respond -> store_cache
   any node error -> fail (localized message, DB errors identified separately)
```

Every node is wrapped so exceptions become a graceful reply instead of a 500.

## Tools

`search_products`, `filter_products`, `compare_products`, `calculate_value_score`, `retrieve_reviews`, `save_preferences`, `get_user_preferences`, `build_shopping_list` (in `agents/tools/tools.py`), plus `semantic_search` used as a fallback when structured search returns nothing.

## Requirement extraction and memory

`services/requirement_service.py` extracts intent, category, budget (supports `25,000`, `25k`, `25 ألف`, ranges), brands, priorities, must-have features and named products from Arabic or English text. Extracted values are merged into the stored `UserPreference` row for the session, so "What if my budget becomes 30K?" keeps brands and priorities and only changes the budget.

## Value score

```
Value Score = 30% Price + 25% Performance + 20% Specifications + 15% User Preferences + 10% Reviews
```

All components are 0-100:

- **Price**: 85% performance-squared per EGP (normalized across the candidates) + 15% cheapness. A pure "cheapest wins" price term made 8,500 EGP phones win gaming queries, so value-for-money is used instead.
- **Performance**: mean of the metrics for the user's priorities (camera, gaming, battery...), blended 80/20 with the general performance score.
- **Specifications**: absolute normalized spec composite per category.
- **Preferences**: share of satisfied constraints (preferred brand, within budget, must-have features); 50 when the user stated none.
- **Reviews**: 50% product rating + 50% average of stored review ratings.

Weights live in `services/scoring_service.py` and can be tuned.

## RAG

Product data is cleaned and split category-aware into an overview chunk and a category-specific specs chunk; every review is one chunk. Metadata (`category`, `brand`, `price`, `available`, `product_id`) enables filtering. Prices are metadata only, never in chunk text, so the model cannot quote a price from retrieved text. Embeddings use a deterministic local hashing embedder (word + character n-gram, 384 dims) so the project runs offline; replace `rag/embeddings.py` with a neural embedding model for production semantic quality. If Chroma fails, reviews fall back to the relational DB and the user is told.

## Caching and freshness

The agent result is cached in Redis keyed by a hash of the effective requirements (intent, category, budget, brands, priorities, product ids, language). Default TTL is 600 seconds (`CACHE_TTL_SECONDS`): within the TTL a price change in the catalog is not reflected, in exchange for faster answers and less DB/RAG load. Degraded answers (RAG fallback) and clarification messages are never cached. The TTL should be tuned against how often real prices change.
