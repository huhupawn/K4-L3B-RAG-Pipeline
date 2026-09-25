"""
Task 5 — Semantic search.

Embed query bằng chính hàm của Task 4, query ChromaDB và đổi cosine distance
thành similarity. Output phải theo SearchResult, sort giảm dần và không quá top_k.
"""

from .task4_chunking_indexing import embed_texts, get_collection


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Trả về dense SearchResult theo score giảm dần.
    
    - Dùng chung embed_texts() với Task 4 để tránh lệch model/dimension.
    - ChromaDB dùng cosine distance, convert: similarity = 1 - distance.
    - Results được sort giảm dần theo score, không trùng ID, không quá top_k.
    """
    # Embed query bằng cùng hàm Task 4
    query_vector = embed_texts([query])[0]
    
    collection = get_collection()
    response = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )
    
    results = []
    for item_id, content, metadata, distance in zip(
        response["ids"][0],
        response["documents"][0],
        response["metadatas"][0],
        response["distances"][0],
    ):
        # Convert cosine distance (0=identical, 2=opposite) → similarity (1=identical, -1=opposite)
        # Clamp để tránh floating point artifacts
        similarity = max(0.0, 1.0 - distance)
        results.append({
            "id": item_id,
            "content": content,
            "score": float(similarity),
            "metadata": metadata,
            "retrieval_method": "dense",
        })
    
    # Sort giảm dần theo score
    return sorted(results, key=lambda item: item["score"], reverse=True)[:top_k]


if __name__ == "__main__":
    for result in semantic_search("test query", top_k=3):
        print(result)
