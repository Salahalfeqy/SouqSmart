from app.rag.embeddings import get_embedder
from app.rag.vector_store import PRODUCTS, REVIEWS, get_collection


class RAGError(Exception):
    pass


def build_where(category=None, brands=None, min_price=None, max_price=None, product_ids=None, available_only=False):
    clauses = []
    if category:
        clauses.append({"category": category})
    if brands:
        clauses.append({"brand": {"$in": list(brands)}} if len(brands) > 1 else {"brand": brands[0]})
    if min_price is not None:
        clauses.append({"price": {"$gte": float(min_price)}})
    if max_price is not None:
        clauses.append({"price": {"$lte": float(max_price)}})
    if product_ids:
        clauses.append({"product_id": {"$in": [int(i) for i in product_ids]}} if len(product_ids) > 1 else {"product_id": int(product_ids[0])})
    if available_only:
        clauses.append({"available": True})
    if not clauses:
        return None
    return clauses[0] if len(clauses) == 1 else {"$and": clauses}


def _query(collection_name, query, where, k):
    try:
        collection = get_collection(collection_name)
        if collection.count() == 0:
            return []
        res = collection.query(query_embeddings=[get_embedder().embed(query)], n_results=k, where=where)
    except Exception as exc:
        raise RAGError(str(exc)) from exc
    out = []
    for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        out.append({"text": doc, "metadata": meta, "score": round(1 - float(dist), 4)})
    return out


def semantic_product_search(query, category=None, brands=None, min_price=None, max_price=None, available_only=False, k=10):
    where = build_where(category, brands, min_price, max_price, None, available_only)
    hits = _query(PRODUCTS, query, where, k * 2)
    best = {}
    for h in hits:
        pid = h["metadata"]["product_id"]
        if pid not in best or h["score"] > best[pid]["score"]:
            best[pid] = {"product_id": pid, "score": h["score"], "chunk_type": h["metadata"]["chunk_type"]}
    return sorted(best.values(), key=lambda x: -x["score"])[:k]


def retrieve_reviews(query, product_ids, k_per_product=2):
    results = {}
    for pid in product_ids:
        hits = _query(REVIEWS, query, build_where(product_ids=[pid]), k_per_product)
        results[pid] = [{"text": h["text"].split("review: ", 1)[-1], "rating": h["metadata"]["rating"], "source": h["metadata"].get("source", ""), "score": h["score"]} for h in hits]
    return results
