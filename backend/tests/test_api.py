def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_products_list_and_filters(client):
    r = client.get("/api/v1/products", params={"category": "laptop", "max_price": 30000})
    assert r.status_code == 200
    data = r.json()
    assert data and all(p["category"] == "laptop" and p["price"] <= 30000 for p in data)
    assert len(client.get("/api/v1/products", params={"limit": 200}).json()) >= 30


def test_product_not_found(client):
    assert client.get("/api/v1/products/99999").status_code == 404


def test_search(client):
    r = client.post("/api/v1/products/search", json={"query": "samsung camera", "category": "phone", "max_price": 25000})
    assert r.status_code == 200
    assert all(p["brand"] == "Samsung" for p in r.json()[:3])
    bad = client.post("/api/v1/products/search", json={"min_price": 10, "max_price": 5})
    assert bad.status_code == 422


def test_compare_endpoint(client):
    r = client.post("/api/v1/products/compare", json={"product_ids": [1, 7, 13]})
    assert r.status_code == 200
    body = r.json()
    assert len(body["products"]) == 3 and body["winner_id"]
    assert client.post("/api/v1/products/compare", json={"product_ids": [99999]}).status_code == 404


def test_chat_and_cache_headers(client):
    payload = {"session_id": "api-1", "message": "Best phone under 25000 for gaming?"}
    first = client.post("/api/v1/chat", json=payload).json()
    second = client.post("/api/v1/chat", json=payload).json()
    assert first["cache_hit"] is False and second["cache_hit"] is True
    assert first["payload"]["winner_id"] == second["payload"]["winner_id"]


def test_chat_validation(client):
    assert client.post("/api/v1/chat", json={"session_id": "x", "message": "   "}).status_code == 422
    assert client.post("/api/v1/chat", json={"session_id": "x", "message": "a" * 2000}).status_code == 422


def test_preferences_roundtrip(client):
    client.post("/api/v1/preferences", json={"session_id": "pref-1", "budget": 12000, "preferred_brands": ["Sony"]})
    got = client.get("/api/v1/preferences/pref-1").json()
    assert got["budget"] == 12000 and got["preferred_brands"] == ["Sony"]
    cleared = client.delete("/api/v1/preferences/pref-1").json()
    assert cleared["budget"] is None


def test_sessions_and_messages(client):
    client.post("/api/v1/chat", json={"session_id": "hist-1", "message": "hello"})
    sessions = client.get("/api/v1/sessions").json()
    assert any(s["session_id"] == "hist-1" for s in sessions)
    msgs = client.get("/api/v1/sessions/hist-1/messages").json()
    assert [m["role"] for m in msgs][:2] == ["user", "assistant"]


def test_analytics_reflects_real_activity(client):
    client.post("/api/v1/chat", json={"session_id": "an-1", "message": "phone under 25000 for camera"})
    client.post("/api/v1/chat", json={"session_id": "an-1", "message": "phone under 25000 for camera"})
    data = client.get("/api/v1/analytics").json()
    assert data["total_searches"] >= 2
    assert data["cache"]["hits"] >= 1
    assert data["popular_category"] == "smartphone"
    assert 0 < data["cache"]["hit_rate"] <= 100
