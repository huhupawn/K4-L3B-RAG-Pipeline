"""
Task 9 — Retrieval pipeline hoàn chỉnh.

Luồng xử lý:
    1. Chạy semantic_search và lexical_search.
    2. Fuse hai danh sách bằng RRF đúng một lần.
    3. Lấy best cosine score gốc từ dense results.
    4. Nếu score dưới threshold, thử PageIndex fallback.
    5. Nếu fallback lỗi, trả hybrid results thay vì crash.

Không so sánh threshold với RRF score vì hai thang đo khác nhau.
"""

from .task5_semantic_search import semantic_search
from .task6_lexical_search import lexical_search
from .task7_reranking import rerank_rrf
from .task8_pageindex_vectorless import pageindex_search


SCORE_THRESHOLD = 0.3
DEFAULT_TOP_K = 5


def retrieve(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    score_threshold: float = SCORE_THRESHOLD,
    use_reranking: bool = True,
) -> list[dict]:
    """
    Trả về hybrid hoặc pageindex SearchResult.
    
    Luồng:
    - semantic_search + lexical_search → song song (hiện tại tuần tự)
    - RRF fusion một lần duy nhất
    - Best dense score < threshold → thử PageIndex
    - PageIndex lỗi → trả hybrid thay vì crash
    """
    # Bước 1: Dense search
    dense = semantic_search(query, top_k=top_k * 2)
    
    # Bước 2: Sparse (BM25) search
    sparse = lexical_search(query, top_k=top_k * 2)
    
    # Bước 3: RRF fusion (gọi đúng một lần duy nhất khi use_reranking=True)
    # Gọi RRF kể cả khi sparse trống (RRF xử lý được empty list)
    if use_reranking and dense:
        hybrid = rerank_rrf([dense, sparse], top_k=top_k)
    else:
        # Không dùng reranking → chỉ trả dense thuần
        hybrid = []

    # Bước 4: Kiểm tra confidence của dense search
    best_dense_score = dense[0]["score"] if dense else 0.0
    
    if best_dense_score < score_threshold:
        try:
            fallback = pageindex_search(query, top_k=top_k)
            if fallback:
                return fallback
        except Exception:
            # Fallback lỗi → trả hybrid thay vì crash
            pass
    
    return hybrid[:top_k]


if __name__ == "__main__":
    for result in retrieve("test query", top_k=3):
        print(result)
