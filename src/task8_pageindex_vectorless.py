"""
Task 8 — PageIndex vectorless fallback.

Hướng dẫn:
    1. Đọc PAGEINDEX_API_KEY từ .env.
    2. Upload tài liệu ở định dạng PageIndex hỗ trợ.
    3. Cache document IDs để không upload lại.
    4. Parse kết quả thành SearchResult có method pageindex.

PageIndex là dịch vụ ngoài: cần timeout và xử lý lỗi để pipeline không crash.
"""

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"


def _get_pageindex_client():
    """
    Lazy-init PageIndex client.
    Đặt trong function để tránh import lỗi khi không có API key.
    """
    if not PAGEINDEX_API_KEY:
        raise RuntimeError("PAGEINDEX_API_KEY not configured")
    # Placeholder — thay bằng SDK thực tế của nhóm
    raise NotImplementedError(
        "PageIndex integration not implemented. "
        "Set PAGEINDEX_API_KEY and implement upload/search logic."
    )


# ── Document upload & cache ──────────────────────────────────────────────────

def upload_documents() -> None:
    """
    Upload tài liệu và lưu document IDs để tái sử dụng.
    Nếu SDK không nhận Markdown, convert sang PDF tạm trước khi upload.
    """
    if not PAGEINDEX_API_KEY:
        return  # Safe no-op

    # TODO: Implement document upload
    raise NotImplementedError("Implement upload_documents")


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """
    Trả về pageindex SearchResult.
    
    Nếu PageIndex không khả dụng hoặc lỗi, raise exception để
    pipeline fallback xử lý (theo contract: không crash UI).
    """
    if not PAGEINDEX_API_KEY:
        raise RuntimeError("PAGEINDEX_API_KEY not configured")

    # TODO: Implement PageIndex search
    # Mỗi result cần: id, content, score, metadata, retrieval_method.
    # Nếu API không trả score, gán score giảm dần theo rank.
    raise NotImplementedError("Implement pageindex_search")


if __name__ == "__main__":
    upload_documents()
