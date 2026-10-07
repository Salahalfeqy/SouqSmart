# SouqSmart 🛍️

> **AI Shopping and Price Comparison Assistant for Egyptian Shoppers**
> 
> One conversation replaces searching several sites. SouqSmart understands your request (Arabic or English), searches the catalog intelligently, and recommends the best products based on your budget, preferences, and priorities.

---

## 🎯 Status & Badges

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat-square&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-Web%20UI-FF4B4B?style=flat-square&logo=streamlit)
![LangGraph](https://img.shields.io/badge/LangGraph-AI%20Agent-00D084?style=flat-square)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791?style=flat-square&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=flat-square&logo=docker)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)

---

## 📚 Tech Stack

### Core Technologies

| Layer | Technology | Version |
|-------|-----------|---------|
| **Backend Framework** | FastAPI | ≥0.110 |
| **AI Agent** | LangGraph | ≥0.2 |
| **RAG Engine** | ChromaDB | ≥0.5 |
| **Database** | PostgreSQL (SQLite fallback) | 16-Alpine |
| **Cache Layer** | Redis | 7-Alpine |
| **Frontend UI** | Streamlit | Latest |
| **ORM** | SQLAlchemy | ≥2.0 |
| **Runtime** | Uvicorn | ≥0.29 |
| **Server** | Python | 3.10+ |
| **Containerization** | Docker | Latest |

### Key Dependencies

**Backend:**
- **LLM Integration**: LangChain Core (≥0.3), LangGraph (≥0.2)
- **Data Processing**: Pydantic (≥2.6), SQLAlchemy (≥2.0)
- **Database**: psycopg2-binary (≥2.9), Redis (≥5.0)
- **Vector Store**: ChromaDB (≥0.5)
- **Testing**: pytest (≥8.0), httpx (≥0.27)
- **HTTP**: requests (≥2.31)

**Frontend:**
- Streamlit (UI framework)
- Plotly (Dashboard & visualizations)

### Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                    SouqSmart System                           │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌─────────────┐         ┌──────────────┐                    │
│  │  Streamlit  │◄────────┤  FastAPI v1  │                    │
│  │     UI      │         │     API      │                    │
│  └─────────────┘         └──────┬───────┘                    │
│                                 │                             │
│        ┌────────────────────────┼────────────────────┐       │
│        │                        │                    │       │
│   ┌────▼────────┐    ┌─────────▼──────┐   ┌────────▼─┐     │
│   │  LangGraph  │    │  ChromaDB      │   │  Redis   │     │
│   │  Agent (14  │◄───┤  Vector Store  │   │  Cache   │     │
│   │   nodes,    │    │  (RAG)         │   │ (TTL)    │     │
│   │   8 tools)  │    └────────────────┘   └──────────┘     │
│   └────┬────────┘                                            │
│        │                                                      │
│   ┌────▼────────────────────────┐                           │
│   │   PostgreSQL Database        │                           │
│   │ - Products                   │                           │
│   │ - User Preferences           │                           │
│   │ - Reviews                    │                           │
│   │ - Search History             │                           │
│   │ - Chat Messages              │                           │
│   └──────────────────────────────┘                           │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Project Structure

```
SouqSmart/
├── backend/                          # FastAPI backend
│   ├── app/
│   │   ├── main.py                  # Application entry point
│   │   ├── config.py                # Configuration management
│   │   ├── agents/                  # LangGraph agent implementation
│   │   │   ├── agent.py             # Main agent orchestration
│   │   │   ├── tools.py             # 8 agent tools
│   │   │   └── nodes.py             # 14 graph nodes
│   │   ├── api/                     # API endpoints (/api/v1)
│   │   │   ├── routes.py            # Route definitions
│   │   │   └── v1/                  # Versioned endpoints
│   │   ├── rag/                     # RAG pipeline
│   │   │   ├── retriever.py         # Document retrieval
│   │   │   ├── chunker.py           # Category-aware chunking
│   │   │   └── vector_store.py      # ChromaDB integration
│   │   ├── services/                # Business logic
│   │   │   ├── requirement_service.py  # Intent extraction
│   │   │   ├── scoring_service.py   # Value scoring
│   │   │   ├── search_service.py    # Product search
│   │   │   └── cache_service.py     # Redis caching
│   │   ├── database/                # ORM & models
│   │   │   ├── models.py            # SQLAlchemy models
│   │   │   ├── session.py           # DB session management
│   │   │   └── schema.py            # Pydantic schemas
│   │   └── schemas/                 # Request/response models
│   ├── tests/                       # Pytest suite (36+ tests)
│   ├── Dockerfile                   # Backend container
│   └── requirements.txt             # Python dependencies
│
├── frontend/                         # Streamlit UI
│   ├── app.py                       # Main Streamlit app
│   ├── components/                  # Reusable UI components
│   │   ├── chat.py                  # Chat interface
│   │   ├── product_cards.py         # Product display
│   │   └── dashboard.py             # Analytics dashboard
│   ├── views/                       # Page views
│   │   ├── chat_view.py             # Chat page
│   │   └── analytics_view.py        # Analytics page
│   ├── services/                    # API client utilities
│   ├── .streamlit/                  # Streamlit config
│   ├── Dockerfile                   # Frontend container
│   └── requirements.txt             # Python dependencies
│
├── rag/                             # Shared RAG utilities
│   ├── documents.py                 # Document loaders
│   └── embeddings.py                # Embedding utilities
│
├── data/                            # Sample data
│   ├── products/                    # Product catalog
│   │   └── products.json            # 46 products (phones, laptops, headphones)
│   └── reviews/                     # Review data
│       └── reviews.json             # 218 synthetic reviews
│
├── scripts/                         # Utility scripts
│   ├── evaluate.py                  # Evaluation suite
│   ├── seed_db.py                   # Database seeding
│   └── generate_embeddings.py       # Vector store setup
│
├── docs/                            # Documentation
│   ├── architecture.md              # System architecture
│   ├── database.md                  # Database schema
│   ├── api.md                       # API reference
│   ├── evaluation.md                # Evaluation methodology
│   └── evaluation_results.json      # Test results
│
├── docker-compose.yml               # Multi-container orchestration
├── .env.example                     # Environment template
├── .gitignore                       # Git ignore rules
└── README.md                        # This file
```

---

## 🎯 Project Overview & Features

### What SouqSmart Does

SouqSmart is an **AI-powered shopping assistant** that bridges the gap between Egyptian shoppers and the fragmented e-commerce landscape. Instead of visiting multiple sites to compare prices, check availability, and read reviews, users simply have a conversation with SouqSmart—in Arabic or English—and get intelligent, personalized recommendations.

### Key Features

#### 1. **Natural Language Understanding**
   - Bilingual support: Arabic and English
   - Understands budget specifications: "25,000", "25k", "25 ألف", "25k-30k"
   - Extracts intent: recommendation, comparison, reviews, shopping list
   - Recognizes product categories: smartphones, laptops, headphones
   - Identifies brands, features, and priorities automatically

#### 2. **Intelligent Product Search**
   - Category-aware RAG with ChromaDB
   - Semantic search on product overviews and specs
   - Metadata filtering (price, availability, brand)
   - Fallback to rule-based search if RAG fails
   - Results paginated with offset/limit support

#### 3. **Smart Product Comparison**
   - Compare 1-6 products side-by-side
   - **Value Score Algorithm** (proprietary):
     - 30% Price (value-for-money normalized)
     - 25% Performance (user priorities blended)
     - 20% Specifications (category-specific composites)
     - 15% User Preferences (constraint satisfaction)
     - 10% Reviews (rating aggregation)
   - Identifies winner based on requirements
   - Explains reasoning in natural language

#### 4. **AI Agent Architecture**
   - **LangGraph** with 14 nodes and 8 tools
   - Multi-turn memory with session support
   - Context preservation across conversations
   - Graceful error handling with localized messages
   - Cache-aware to avoid redundant computations

#### 5. **Preference Learning**
   - Automatic extraction: preferred brands, budget range, must-have features, priorities
   - Per-session storage in PostgreSQL
   - Used for personalized filtering and scoring
   - Can be saved or cleared per session

#### 6. **Caching & Performance**
   - Redis TTL cache (default: 600 seconds)
   - Cache key: hash of effective requirements
   - Cache-hit tracking for analytics
   - In-memory fallback if Redis unavailable
   - Response time tracking per query

#### 7. **Dashboard & Analytics**
   - Real-time KPIs: total queries, cache hit rate, avg response time
   - Category breakdown charts
   - Search history with intent distribution
   - Comparison frequency trends
   - Cache performance visualization

#### 8. **Data Safety**
   - Prices sourced only from verified database
   - Missing prices shown as "no verified price available"
   - Out-of-stock products excluded from recommendations
   - Nullable price field prevents speculation
   - Synthetic data for safe testing

### Use Cases

| Use Case | How SouqSmart Helps |
|----------|-------------------|
| **Budget Shopping** | "Best phone under 5000 EGP?" → Filters, scores, recommends |
| **Brand Comparison** | "Compare Samsung vs iPhone for gaming" → Side-by-side with value scores |
| **Feature Matching** | "I need a laptop with 16GB RAM, gaming GPU" → Extracts specs, searches, ranks |
| **Price Tracking** | "Show me all phones 20k-25k" → Filters by price, sorts by value |
| **Review Research** | "What do people say about the Pixel 8?" → Retrieves and summarizes reviews |
| **Shopping List** | "Add these to my wishlist: [products]" → Builds and stores list |

---

## 📊 Entity Relationship Diagram (ERD)

### Database Schema

```mermaid
erDiagram
    USERS ||--o{ USER_PREFERENCES : has
    USERS ||--o{ SEARCH_HISTORY : performs
    USERS ||--o{ COMPARISON_HISTORY : performs
    USERS ||--o{ CHAT_MESSAGES : sends
    PRODUCTS ||--o{ PRODUCT_SPECIFICATIONS : has
    PRODUCTS ||--o{ REVIEWS : receives
    COMPARISON_HISTORY ||--o{ PRODUCTS : compares

    USERS {
        int id PK
        string session_id UK
        datetime created_at
    }

    USER_PREFERENCES {
        int id PK
        int user_id FK
        decimal budget
        string preferred_brands
        string preferred_categories
        string must_have_features
        string priority_features
        datetime updated_at
    }

    PRODUCTS {
        int id PK
        string name
        string brand
        string category
        decimal price "nullable"
        decimal old_price
        string description
        float rating
        int stock
        string source
        string url
        string image_url
        datetime created_at
        datetime updated_at
    }

    PRODUCT_SPECIFICATIONS {
        int id PK
        int product_id FK
        string key
        string value "JSON"
    }

    REVIEWS {
        int id PK
        int product_id FK
        string review_text
        float rating
        string source
        datetime created_at
    }

    SEARCH_HISTORY {
        int id PK
        int user_id FK
        string query
        string category
        string brand
        string intent
        float response_time
        boolean cache_hit
        datetime created_at
    }

    COMPARISON_HISTORY {
        int id PK
        int user_id FK
        string product_ids
        int selected_product_id FK
        datetime created_at
    }

    CHAT_MESSAGES {
        int id PK
        int user_id FK
        string role
        string content
        string payload "JSON"
        datetime created_at
    }
```

### Database Diagram (Visual)

![Database ERD](docs/erd-diagram.png)

**Schema Highlights:**
- **Products**: Core catalog with nullable price (missing prices aren't guessed)
- **Product Specifications**: Flexible key-value JSON storage for specs
- **Reviews**: Product feedback with ratings
- **User Preferences**: Session-based preference storage
- **Search History**: Analytics on queries, intents, and performance
- **Comparison History**: Tracks product comparisons and selections
- **Chat Messages**: Full conversation history per session

---

## 🚀 Getting Started

### Prerequisites

Before you start, ensure you have:

| Requirement | Version | Purpose |
|---|---|---|
| **Python** | 3.10+ | Runtime environment |
| **Docker** | 20.10+ | Container orchestration |
| **Docker Compose** | 1.29+ | Multi-container setup |
| **Git** | Latest | Version control |
| **Git LFS** (optional) | Latest | Large file storage (for models) |

**System Requirements:**
- RAM: 4 GB minimum (8 GB recommended)
- Disk Space: 2 GB available
- OS: Windows, macOS, or Linux

### Installation Steps

#### Option 1️⃣: Docker Compose (Recommended - Easiest)

```bash
# Step 1: Clone the repository
git clone https://github.com/Salahalfeqy/SouqSmart.git
cd SouqSmart

# Step 2: Copy environment template
cp .env.example .env

# Step 3: Edit .env (optional - customize if needed)
# nano .env
# Set OPENAI_API_KEY if you have one (optional)

# Step 4: Build and run with Docker
docker compose up --build

# Step 5: Access the application
# UI:  http://localhost:8501
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

**What this does:**
- Pulls PostgreSQL 16 image
- Pulls Redis 7 image
- Builds backend container
- Builds frontend container
- Creates persistent volumes for DB and vector store
- Orchestrates service startup order
- Applies health checks

**Docker Compose Services:**
```
postgres   → Database (port 5432, internal only)
redis      → Cache (port 6379, internal only)
backend    → FastAPI (port 8000, http://localhost:8000)
frontend   → Streamlit (port 8501, http://localhost:8501)
```

#### Option 2️⃣: Local Python Development

**Prerequisites:**
- PostgreSQL 12+ running locally (or skip and use SQLite)
- Redis 6+ running locally (or skip for in-memory fallback)

```bash
# Step 1: Clone and navigate
git clone https://github.com/Salahalfeqy/SouqSmart.git
cd SouqSmart

# Step 2: Create virtual environment
python -m venv venv

# Activate it:
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Step 3: Copy environment file
cp .env.example .env

# Step 4: Install backend dependencies
cd backend
pip install -r requirements.txt

# Step 5: Initialize database (optional - creates SQLite if no DATABASE_URL)
# python scripts/seed_db.py

# Step 6: Start backend (from backend/ directory)
uvicorn app.main:app --port 8000 --reload

# In a new terminal:
# Step 7: Install frontend dependencies
cd frontend
pip install -r requirements.txt

# Step 8: Start frontend (set API_URL to backend)
API_URL=http://localhost:8000 streamlit run app.py
```

**Environment Variables for Local Setup:**
```bash
# Database (optional - uses SQLite if not set)
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/souqsmart

# Redis (optional - uses in-memory if not set)
REDIS_URL=redis://localhost:6379/0

# LLM (optional - uses rule-based extraction if not set)
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini

# Caching
CACHE_TTL_SECONDS=600
```

#### Option 3️⃣: Development with Auto-Reload

```bash
# Backend with auto-reload
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend with Streamlit rerun
cd frontend
pip install -r requirements.txt
streamlit run app.py --logger.level=debug
```

---

## ⚙️ Environment Variables

### Configuration Reference

Create a `.env` file in the project root (copy from `.env.example`):

```bash
# PostgreSQL Database (optional - uses SQLite if empty)
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/souqsmart

# Redis Cache (optional - in-memory fallback if empty)
REDIS_URL=redis://localhost:6379/0
CACHE_TTL_SECONDS=600

# OpenAI API (optional - uses rule-based extraction if empty)
OPENAI_API_KEY=sk-your-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini

# PostgreSQL Docker Defaults
POSTGRES_PASSWORD=souqsmart
POSTGRES_USER=souqsmart
POSTGRES_DB=souqsmart
```

### Environment Variables Table

| Variable | Type | Required | Default | Example | Description |
|---|---|---|---|---|---|
| `DATABASE_URL` | string | ❌ | SQLite `./souqsmart.db` | `postgresql+psycopg2://user:pass@localhost:5432/souqsmart` | PostgreSQL connection string |
| `REDIS_URL` | string | ❌ | In-memory cache | `redis://localhost:6379/0` | Redis connection for caching |
| `CACHE_TTL_SECONDS` | int | ❌ | 600 | 300-1800 | Cache expiration time in seconds |
| `OPENAI_API_KEY` | string | ❌ | None (rule-based) | `sk-proj-...` | OpenAI API key for LLM |
| `OPENAI_BASE_URL` | string | ❌ | `https://api.openai.com/v1` | Custom endpoint | LLM provider base URL |
| `LLM_MODEL` | string | ❌ | `gpt-4o-mini` | `gpt-4`, `gpt-3.5-turbo` | LLM model identifier |
| `POSTGRES_PASSWORD` | string | ❌ | `souqsmart` | Your secure password | PostgreSQL password (Docker) |
| `POSTGRES_USER` | string | ❌ | `souqsmart` | DB username | PostgreSQL user (Docker) |
| `POSTGRES_DB` | string | ❌ | `souqsmart` | DB name | PostgreSQL database name (Docker) |

### Configuration Priority

1. **Environment Variables** (highest priority)
2. **.env File**
3. **Docker Compose `.env_file`**
4. **Defaults** (lowest priority)

---

## 📖 Usage & API Endpoints

### Quickstart Examples

#### 1. Start a Chat Conversation

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user123",
    "message": "Best phone under 25000 for gaming?"
  }'
```

**Response:**
```json
{
  "reply": "I found 3 great gaming phones under 25,000 EGP...",
  "payload": {
    "products": [
      {
        "id": 1,
        "name": "Redmi Note 13",
        "price": 18500,
        "value_score": 92.5
      }
    ],
    "winner": {
      "id": 1,
      "reason": "Best value-for-money with high gaming performance"
    }
  },
  "preferences": {
    "budget": 25000,
    "priority_features": ["gaming", "performance"]
  },
  "cache_hit": false,
  "response_time": 1.234,
  "trace": "search -> score_rank -> compare -> reviews -> respond"
}
```

#### 2. Search Products

```bash
curl -X POST http://localhost:8000/api/v1/products/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "gaming laptop",
    "category": "laptops",
    "min_price": 10000,
    "max_price": 50000,
    "available_only": true,
    "limit": 5
  }'
```

#### 3. Compare Products

```bash
curl -X POST http://localhost:8000/api/v1/products/compare \
  -H "Content-Type: application/json" \
  -d '{
    "product_ids": [1, 2, 3],
    "session_id": "user123",
    "budget": 25000,
    "priority_features": ["performance", "camera"],
    "preferred_brands": ["Samsung", "iPhone"]
  }'
```

#### 4. Get Analytics

```bash
curl http://localhost:8000/api/v1/analytics
```

### API Reference

**Base Path:** `/api/v1`  
**Interactive Docs:** `/docs` (Swagger UI)  
**Health Check:** `/health`

#### Core Endpoints

| Method | Endpoint | Purpose | Request Body |
|---|---|---|---|
| **GET** | `/products` | List products with filters | Query params: `category`, `brand`, `min_price`, `max_price`, `available_only`, `limit`, `offset` |
| **GET** | `/products/{id}` | Get single product | — |
| **POST** | `/products/search` | Search with natural language | `query`, `category`, `brands`, `min_price`, `max_price`, `available_only`, `limit` |
| **POST** | `/products/compare` | Compare 1-6 products | `product_ids`, `session_id`, `budget`, `priority_features`, `preferred_brands` |
| **POST** | `/chat` | Send message to agent | `session_id`, `message` |
| **GET** | `/preferences/{session_id}` | Get user preferences | — |
| **POST** | `/preferences` | Save preferences | `session_id`, `budget`, `preferred_brands`, `preferred_categories`, `must_have_features`, `priority_features` |
| **DELETE** | `/preferences/{session_id}` | Clear preferences | — |
| **GET** | `/sessions` | List conversations | Query: `limit`, `offset` |
| **GET** | `/sessions/{session_id}/messages` | Get messages | Query: `limit`, `offset` |
| **GET** | `/analytics` | Get KPIs and charts | — |
| **POST** | `/analytics/cache/clear` | Clear cache | — |

### Response Format

**Success (200):**
```json
{
  "data": { /* response data */ },
  "success": true,
  "message": "Operation successful"
}
```

**Error (400/500):**
```json
{
  "detail": "Error description",
  "type": "ValidationError" | "DatabaseError" | "RAGError" | "AgentError"
}
```

### Frontend Usage

**Streamlit UI:**
1. Open http://localhost:8501
2. Select "Chat" or "Analytics"
3. **Chat Tab**: Type your question in Arabic or English
4. **Analytics Tab**: View KPIs, search trends, cache metrics

### Command Line Testing

```bash
# Test suite (36 tests)
cd backend
pytest tests -v

# Evaluation script
python scripts/evaluate.py

# Run specific test
pytest tests/test_api.py::test_chat -v
```

---

## 🧪 Testing & Evaluation

### Running Tests

```bash
# Navigate to backend
cd backend

# Run all tests
pytest tests -q

# Run with coverage
pytest tests --cov=app --cov-report=html

# Run specific test file
pytest tests/test_agents.py -v

# Run with markers (if available)
pytest -m "unit" -v
pytest -m "integration" -v
```

### Test Coverage

**36 Tests Cover:**
- ✅ 10 predefined user scenarios
- ✅ Multi-turn conversation memory
- ✅ Price safety enforcement
- ✅ Cache hit/miss logic
- ✅ RAG search accuracy
- ✅ Database fallbacks
- ✅ API endpoints (chat, search, compare, preferences)
- ✅ Error handling and localization
- ✅ Vector store initialization
- ✅ Performance metrics

### Evaluation Script

```bash
python scripts/evaluate.py
```

Generates `docs/evaluation_results.json` with:
- Scenario success rates
- Average response times
- Cache hit percentages
- RAG relevance scores
- Agent path analysis

**Example Results:**
```json
{
  "total_scenarios": 10,
  "passed": 10,
  "failed": 0,
  "average_response_time": 1.24,
  "cache_hit_rate": 0.35,
  "scenarios": [
    {
      "name": "Best phone under 25000 for gaming",
      "status": "passed",
      "response_time": 1.5,
      "cache_hit": false
    }
  ]
}
```

---

## 📊 Data & Database

### Sample Data

The project includes **synthetic sample data** for safe testing:

- **Products**: 46 products
  - 18 Smartphones (various brands)
  - 15 Laptops (gaming, ultrabooks, workstations)
  - 12 Headphones (wireless, gaming, professional)
  
- **Reviews**: 218 synthetic reviews
  - Generated with realistic ratings and feedback
  - Associated with products
  - Safe for demonstration purposes

**Files:**
- `data/products/products.json` - Product catalog
- `data/reviews/reviews.json` - Review collection

**Note:** Prices, stock, and reviews are **synthetic sample data** for demonstration. Production deployment should integrate real e-commerce catalogs.

### Database Schema

**Tables (PostgreSQL / SQLite):**

```sql
-- Products with nullable price
products (
  id, name, brand, category, 
  price (nullable), old_price, 
  description, rating, stock, 
  source, url, image_url, 
  created_at, updated_at
)

-- Flexible specifications
product_specifications (
  id, product_id, key, 
  value (JSON string)
)

-- Reviews
reviews (
  id, product_id, review_text, 
  rating, source, created_at
)

-- Users & preferences
users (id, session_id, created_at)
user_preferences (
  budget, preferred_brands, 
  preferred_categories, 
  must_have_features, 
  priority_features, 
  updated_at
)

-- Analytics
search_history (
  query, category, brand, intent, 
  response_time, cache_hit, 
  created_at
)
comparison_history (
  product_ids, selected_product_id, 
  created_at
)
chat_messages (
  role, content, payload (JSON), 
  created_at
)
```

See `docs/database.md` for detailed schema.

---

## 🤝 Contributing

We welcome contributions! Here's how to get involved:

### Contribution Guidelines

1. **Fork the Repository**
   ```bash
   git clone https://github.com/YourUsername/SouqSmart.git
   cd SouqSmart
   ```

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Your Changes**
   - Write clean, documented code
   - Follow PEP 8 style guide
   - Add/update tests for new functionality
   - Update documentation as needed

4. **Test Your Changes**
   ```bash
   cd backend
   pytest tests -q
   ```

5. **Commit and Push**
   ```bash
   git add .
   git commit -m "Add: [Feature description]"
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Describe your changes clearly
   - Reference any related issues
   - Include test results

### Areas for Contribution

- 🐛 **Bug Fixes**: Report and fix issues
- 📚 **Documentation**: Improve guides and API docs
- 🧪 **Tests**: Increase coverage and add edge cases
- 🎨 **Frontend**: UI/UX improvements in Streamlit
- ⚡ **Performance**: Optimize queries and caching
- 🌍 **Localization**: Support more languages
- 🔌 **Integrations**: Add new e-commerce sources
- 📊 **Analytics**: Enhanced dashboards and metrics

### Code Standards

- **Language**: English (code and comments)
- **Style**: PEP 8 (use `black` for formatting)
- **Docstrings**: Google-style for all functions
- **Type Hints**: Use Python type annotations
- **Testing**: Minimum 80% coverage
- **Commits**: Conventional Commits format

### Development Workflow

```bash
# Install dev dependencies
pip install -r backend/requirements.txt -r frontend/requirements.txt
pip install black pytest-cov

# Format code
black backend/ frontend/

# Run linter
flake8 backend/

# Run tests
pytest backend/tests -q --cov=app
```

---

## 📝 License

This project is licensed under the **MIT License**.

### MIT License Summary

- ✅ **Personal Use**: Use the software for personal projects
- ✅ **Commercial Use**: Use in commercial products
- ✅ **Modification**: Modify and distribute freely
- ✅ **Distribution**: Share modified versions
- ❌ **Liability**: No warranty; use at your own risk
- ❌ **Warranty**: Provided as-is

**Full License Text:** See [LICENSE](LICENSE) file in repository

---

## 📞 Support & Contact

### Getting Help

- **GitHub Issues**: [Report bugs or request features](https://github.com/Salahalfeqy/SouqSmart/issues)
- **Discussions**: [Ask questions and discuss](https://github.com/Salahalfeqy/SouqSmart/discussions)
- **Documentation**: Check [docs/](docs/) folder for detailed guides

### Author

**Salahalfeqy**
- GitHub: [@Salahalfeqy](https://github.com/Salahalfeqy)
- Repository: [SouqSmart](https://github.com/Salahalfeqy/SouqSmart)

### Project Info

- **Built For**: DEPI Generative & Agentic AI Systems Capstone
- **Focus**: Agent + RAG + UI/Dashboard + Deployment
- **Status**: 🟢 Active Development
- **Last Updated**: October 2026

---

## 📚 Documentation

Full documentation available in `docs/`:

| Document | Content |
|----------|---------|
| **architecture.md** | System design, agent flow, RAG pipeline, value scoring |
| **database.md** | Schema definitions, relationships, constraints |
| **api.md** | Endpoint reference with examples |
| **evaluation.md** | Testing methodology and metrics |
| **evaluation_results.json** | Actual test results and benchmarks |

---

## 🔒 Security Notes

### Price Safety
- Prices sourced only from PostgreSQL (never guessed)
- Missing prices shown as "no verified price available"
- Out-of-stock products excluded from recommendations
- Value scoring prevents low-quality results

### API Security
- No authentication required (demo mode)
- For production: add JWT or API key auth
- CORS configured for frontend access
- Input validation on all endpoints

### Data Privacy
- Sample data is synthetic
- Session IDs tracked but not linked to personal info
- User preferences stored locally in session
- Consider GDPR compliance for production

---

## 🚀 Deployment

### Production Considerations

1. **Database**: Use managed PostgreSQL (e.g., AWS RDS)
2. **Cache**: Use managed Redis (e.g., AWS ElastiCache)
3. **LLM**: Configure production OpenAI API with rate limits
4. **Monitoring**: Add logging and APM tools
5. **Security**: Add authentication, CORS, rate limiting
6. **Scaling**: Use Kubernetes or container orchestration

### Docker Production Checklist

- [ ] Set strong `POSTGRES_PASSWORD`
- [ ] Use secrets manager for API keys
- [ ] Configure environment for your LLM provider
- [ ] Set appropriate `CACHE_TTL_SECONDS`
- [ ] Enable health checks
- [ ] Add logging and monitoring
- [ ] Test failover scenarios
- [ ] Document deployment process

---

## 📈 Project Statistics

| Metric | Value |
|--------|-------|
| **Primary Language** | Python (99.5%) |
| **Backend Framework** | FastAPI |
| **AI Framework** | LangGraph (14 nodes, 8 tools) |
| **Database** | PostgreSQL + SQLite fallback |
| **Frontend** | Streamlit + Plotly |
| **Tests** | 36+ pytest tests |
| **Sample Products** | 46 (phones, laptops, headphones) |
| **Sample Reviews** | 218 synthetic |
| **Cache Backend** | Redis + in-memory fallback |
| **Vector Store** | ChromaDB |
| **Container Support** | Docker Compose |
| **Status** | 🟢 Active |

---

**Built with ❤️ by the SouqSmart team**

**Last Updated**: October 2026  
**Version**: 1.0.0  
**License**: MIT

---

### Quick Links

- 🏠 [Repository](https://github.com/Salahalfeqy/SouqSmart)
- 📖 [Documentation](docs/)
- 🐛 [Issues](https://github.com/Salahalfeqy/SouqSmart/issues)
- 💡 [Discussions](https://github.com/Salahalfeqy/SouqSmart/discussions)
- 📄 [License](LICENSE)

---

**Let's make shopping smarter! 🛍️✨**
