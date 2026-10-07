# SouqSmart

AI shopping and price comparison assistant for Egyptian shoppers. One conversation replaces searching several sites: SouqSmart understands the request (Arabic or English), searches the catalog, retrieves reviews with RAG, compares at least three products, calculates a value score and recommends the best option while remembering preferences across turns.

Built for the DEPI Generative & Agentic AI Systems capstone: **Agent + RAG + UI/Dashboard + Deployment**.

## Stack

| Layer | Technology |
|---|---|
| Agent | LangGraph (14 nodes, 8 tools) |
| RAG | Chroma, category-aware chunking, metadata filters |
| Backend | FastAPI, versioned `/api/v1` |
| Database | PostgreSQL (SQLite fallback for local runs) via SQLAlchemy |
| Cache | Redis with TTL (in-memory fallback if Redis is down) |
| UI | Streamlit chat + Plotly dashboard |
| Deploy | Docker Compose |

## Run with Docker

```bash
cp .env.example .env
docker compose up --build
```

UI: http://localhost:8501 · API docs: http://localhost:8000/docs

## Run locally

```bash
pip install -r backend/requirements.txt -r frontend/requirements.txt
cd backend && uvicorn app.main:app --port 8000
cd frontend && API_URL=http://localhost:8000 streamlit run app.py
```

Without `DATABASE_URL` the backend uses SQLite, and without a reachable Redis it falls back to an in-process cache. The catalog is seeded and the vector index is built automatically on first start.

## Optional LLM

The system works fully without an LLM using rule-based Arabic/English requirement extraction. Set `OPENAI_API_KEY` (and optionally `OPENAI_BASE_URL`, `LLM_MODEL`) to enable an OpenAI-compatible model for extra requirement extraction and the explanation sentence. LLM text is rejected if it contains any price not present in the catalog.

## Price safety

Prices only ever come from the PostgreSQL catalog. Products with no price are shown as "no verified price available", get no value score and are never recommended. Out-of-stock products are never picked as the winner. Tests assert this.

## Tests and evaluation

```bash
cd backend && python -m pytest tests -q
python scripts/evaluate.py
```

36 tests cover the 10 predefined cases, multi-turn memory, price safety, caching, RAG and DB failure fallbacks, and every API endpoint. See `docs/evaluation.md`.

## Data

`data/products/products.json` (46 products: 18 smartphones, 15 laptops, 12 headphones) and `data/reviews/reviews.json` (218 reviews). **Prices, stock and reviews are synthetic sample data for the capstone**, not live market prices. Regenerate with `python scripts/build_catalog.py`, replace with real scraped data using the same schema when available.

## Structure

See `docs/architecture.md`. API reference in `docs/api.md`, schema in `docs/database.md`.
