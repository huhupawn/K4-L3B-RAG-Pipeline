"""
Task 6 — Lexical search bằng BM25.

Dùng cùng corpus chunks với Task 5. BM25 phù hợp với từ khóa chính xác, mã tài
liệu và tên riêng. Output phải theo SearchResult và sort score giảm dần.
"""

from pathlib import Path

from src.task4_chunking_indexing import load_documents, chunk_documents

# CORPUS: list[dict] = []
# Module-level variable để test có thể gán trực tiếp lexical.CORPUS = corpus
_NOT_LOADED = object()
CORPUS: list[dict] = _NOT_LOADED  # type: ignore[assignment]


def _tokenize(text: str) -> list[str]:
    """Tokenize với word + character 3-grams để tăng recall."""
    tokens = []
    for w in text.lower().split():
        w = w.strip(".,;:!?()[]{}\"'")
        if w:
            tokens.append(w)
            if len(w) >= 3:
                for i in range(len(w) - 2):
                    tokens.append(w[i:i+3])
    return tokens


def _load_corpus() -> list[dict]:
    """Lazy-load corpus chunks từ standardized data (không embed)."""
    global CORPUS
    if CORPUS is _NOT_LOADED:
        documents = load_documents()
        CORPUS = chunk_documents(documents)
    return CORPUS


def build_bm25_index(corpus: list[dict] | None = None):
    """
    Tạo BM25 index từ corpus chunks.
    Tokenize bằng word + character n-grams để tăng recall.
    """
    from rank_bm25 import BM25Plus

    if corpus is None:
        corpus = _load_corpus()

    if not corpus:
        raise ValueError("BM25 corpus is empty")

    # BM25Plus với delta=1.0: hoạt động tốt với corpus nhỏ,
    # tránh IDF=0 khi term xuất hiện trong >50% docs (như BM25Okapi gốc)
    tokenized = [_tokenize(item["content"]) for item in corpus]
    return BM25Plus(tokenized, delta=1.0), corpus


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Trả về BM25 SearchResult theo score giảm dần.
    
    - BM25 score không có max cố định, phụ thuộc corpus và query.
    - Chỉ trả kết quả có score > 0 (tránh noise).
    - Sắp xếp giảm dần theo score, giới hạn top_k.
    """
    import numpy as np

    bm25, corpus = build_bm25_index()
    scores = bm25.get_scores(_tokenize(query))
    
    # Lấy top_k indices theo score giảm dần
    if len(scores) == 0:
        return []
    
    # Chỉ lấy những kết quả có score dương
    positive_mask = scores > 0
    if not np.any(positive_mask):
        return []
    
    # Sort indices theo score giảm dần
    sorted_indices = np.argsort(scores)[::-1]
    
    results = []
    for idx in sorted_indices:
        score = scores[idx]
        if score <= 0:
            continue
        item = corpus[idx]
        results.append({
            "id": item["id"],
            "content": item["content"],
            "score": float(score),
            "metadata": item["metadata"],
            "retrieval_method": "bm25",
        })
        if len(results) >= top_k:
            break
    
    return results


if __name__ == "__main__":
    for result in lexical_search("test query", top_k=3):
        print(result)
