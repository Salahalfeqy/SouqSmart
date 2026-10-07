from sqlalchemy.orm import Session

from app.rag.embeddings import get_embedder
from app.rag.vector_store import PRODUCTS, REVIEWS, get_collection, reset_collections
from app.services.product_service import ProductService

CATEGORY_SPEC_TEXT = {
    "smartphone": lambda s: f"Chipset {s.get('chipset')}. RAM {s.get('ram_gb')}GB. Storage {s.get('storage_gb')}GB. Battery {s.get('battery_mah')}mAh. Main camera {s.get('main_camera_mp')}MP. Display {s.get('display_inches')} inch. Camera score {s.get('camera_score')}. Gaming score {s.get('gaming_score')}.",
    "laptop": lambda s: f"Processor {s.get('cpu')}. RAM {s.get('ram_gb')}GB. Storage {s.get('storage_gb')}GB SSD. Graphics {s.get('gpu')}. Display {s.get('display_inches')} inch. Weight {s.get('weight_kg')}kg. Battery {s.get('battery_hours')} hours. Gaming score {s.get('gaming_score')}.",
    "headphones": lambda s: f"Type {s.get('type')}. Active noise cancelling {'yes' if s.get('anc') else 'no'}. Battery {s.get('battery_hours')} hours. Driver {s.get('driver_mm')}mm. Bluetooth {s.get('bluetooth')}.",
}


def product_chunks(p: dict):
    meta = {"product_id": p["id"], "brand": p["brand"], "category": p["category"], "available": bool(p["available"])}
    if p["price"] is not None:
        meta["price"] = float(p["price"])
    spec_text = CATEGORY_SPEC_TEXT[p["category"]](p["specs"])
    yield f"product:{p['id']}:overview", f"{p['name']} by {p['brand']} ({p['category']}). {p['description']}", {**meta, "chunk_type": "overview"}
    yield f"product:{p['id']}:specs", f"{p['name']} specifications. {spec_text}", {**meta, "chunk_type": "specs"}


def ingest(db: Session, rebuild: bool = False) -> dict:
    if rebuild:
        reset_collections()
    embedder = get_embedder()
    service = ProductService(db)
    products = service.list_products(limit=1000)
    by_id = {p["id"]: p for p in products}

    ids, docs, metas = [], [], []
    for p in products:
        for cid, text, meta in product_chunks(p):
            ids.append(cid)
            docs.append(text)
            metas.append(meta)
    if ids:
        get_collection(PRODUCTS).upsert(ids=ids, documents=docs, metadatas=metas, embeddings=embedder.embed_many(docs))

    r_ids, r_docs, r_metas = [], [], []
    for p in products:
        prod = service.repo.get(p["id"])
        for r in prod.reviews:
            meta = {"product_id": p["id"], "brand": p["brand"], "category": p["category"], "rating": int(r.rating), "source": r.source or ""}
            if p["price"] is not None:
                meta["price"] = float(p["price"])
            r_ids.append(f"review:{r.id}")
            r_docs.append(f"{p['name']} review: {r.review_text}")
            r_metas.append(meta)
    if r_ids:
        get_collection(REVIEWS).upsert(ids=r_ids, documents=r_docs, metadatas=r_metas, embeddings=embedder.embed_many(r_docs))
    return {"product_chunks": len(ids), "review_chunks": len(r_ids), "products": len(by_id)}


def ensure_ingested(db: Session) -> dict:
    expected = len(ProductService(db).list_products(limit=1000))
    try:
        have = get_collection(PRODUCTS).count()
    except Exception:
        have = 0
    if expected and have != expected * 2:
        return ingest(db, rebuild=True)
    return {"products": expected, "skipped": True}
