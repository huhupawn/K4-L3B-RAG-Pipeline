"""
Task 4 — Chunking, embedding và indexing.

Hướng dẫn:
    1. Đọc toàn bộ Markdown trong data/standardized/.
    2. Chia văn bản bằng strategy đã chọn.
    3. Embed chunks bằng một provider duy nhất.
    4. Upsert vào ChromaDB với cosine distance.

    Mỗi document/chunk phải theo docs/MODULE_CONTRACTS.md. ID cần ổn định để
chạy lại pipeline không tạo dữ liệu trùng. Task 5 phải dùng chung embed_texts().
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb

# ── Paths ──────────────────────────────────────────────────────────────────
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"

# ── Chunking config (starter values, ghi lại thực tế dùng trong report) ────
# Chunk size 500: đủ ngắn để retrieval chính xác, đủ dài để giữ ngữ cảnh
# Overlap 50: giữ liên kết giữa các chunk liền kề mà không tăng quá nhiều chi phí
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_METHOD = "recursive"

# ── Embedding config (dispatch theo EMBEDDING_PROVIDER trong .env) ───────────
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "gemini")
SKIP_EMBEDDING = os.getenv("SKIP_EMBEDDING", "false").lower() == "true"

# Provider defaults
# sentence_transformers/all-MiniLM-L6-v2 → 384-dim
# gemini-embedding-3-exp → 30768-dim (huge; use 768 below for compatibility)
# openai/text-embedding-3-small → 1536-dim
_EMBEDDING_MODEL_NAME = {
    "sentence_transformers": os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
    "gemini": os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001"),
    "openai": os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
}
_EMBEDDING_DIM = {
    "sentence_transformers": 384,
    "gemini": 3072,   # gemini-embedding-001 output dim
    "openai": 1536,    # text-embedding-3-small output dim
}
EMBEDDING_DIM = _EMBEDDING_DIM.get(EMBEDDING_PROVIDER, 768)

COLLECTION_NAME = "rag_documents"

# ── Cached clients (lazy init) ─────────────────────────────────────────────
_cached_client = None


def _get_client():
    """Lazy-load client/provider theo EMBEDDING_PROVIDER."""
    global _cached_client
    if _cached_client is None:
        if EMBEDDING_PROVIDER == "sentence_transformers":
            from sentence_transformers import SentenceTransformer
            model_name = _EMBEDDING_MODEL_NAME["sentence_transformers"]
            _cached_client = SentenceTransformer(model_name)
        elif EMBEDDING_PROVIDER == "gemini":
            from google import genai
            api_key = os.getenv("GEMINI_API_KEY", "")
            if not api_key:
                raise RuntimeError("GEMINI_API_KEY not configured for Gemini embedding")
            _cached_client = genai.Client(api_key=api_key)
        elif EMBEDDING_PROVIDER == "openai":
            from openai import OpenAI
            api_key = os.getenv("OPENAI_API_KEY", "")
            if not api_key:
                raise RuntimeError("OPENAI_API_KEY not configured for OpenAI embedding")
            _cached_client = OpenAI(api_key=api_key)
        else:
            raise ValueError(f"Unknown EMBEDDING_PROVIDER: {EMBEDDING_PROVIDER}")
    return _cached_client


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Embed danh sách văn bản bằng provider được cấu hình trong .env.
    Đây là điểm dùng chung giữa Task 4 (index) và Task 5 (query).
    Trả về list of vectors, mỗi vector là list of floats, đã normalized (cosine-compatible).
    """
    if SKIP_EMBEDDING:
        import numpy as np
        rng = np.random.default_rng(42)
        return [
            (vec / np.linalg.norm(vec)).tolist()
            for vec in rng.standard_normal((len(texts), EMBEDDING_DIM))
        ]

    if EMBEDDING_PROVIDER == "sentence_transformers":
        client = _get_client()
        vectors = client.encode(texts, normalize_embeddings=True)
        return vectors.tolist()

    elif EMBEDDING_PROVIDER == "gemini":
        from google.genai import types as gt
        client = _get_client()
        model_name = _EMBEDDING_MODEL_NAME["gemini"]
        is_doc = len(texts) > 1
        task_type = "RETRIEVAL_DOCUMENT" if is_doc else "RETRIEVAL_QUERY"
        # Gemini batch limit: 100 texts per request
        BATCH_SIZE = 100
        all_vectors = []
        for i in range(0, len(texts), BATCH_SIZE):
            batch = texts[i : i + BATCH_SIZE]
            result = client.models.embed_content(
                model=model_name,
                contents=batch,
                config=gt.EmbedContentConfig(task_type=task_type),
            )
            all_vectors.extend(emb.values for emb in result.embeddings)
        return all_vectors

    elif EMBEDDING_PROVIDER == "openai":
        client = _get_client()
        model_name = _EMBEDDING_MODEL_NAME["openai"]
        response = client.embeddings.create(
            model=model_name,
            input=texts,
        )
        return [item.embedding for item in response.data]

    raise ValueError(f"Unknown EMBEDDING_PROVIDER: {EMBEDDING_PROVIDER}")


def get_collection():
    """
    Mở Chroma collection dùng cosine distance.
    Tạo mới nếu chưa tồn tại (persistent).
    """
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def load_documents() -> list[dict]:
    """
    Đọc tất cả .md từ data/standardized/ và trả danh sách Document.
    ID được tạo từ relative path để đảm bảo ổn định khi chạy lại.
    """
    documents = []
    for path in sorted(STANDARDIZED_DIR.rglob("*.md")):
        parts = path.parts
        if "legal" in parts:
            doc_type = "legal"
        elif "news" in parts:
            doc_type = "news"
        else:
            doc_type = "other"

        rel_path = path.relative_to(STANDARDIZED_DIR).as_posix()
        title = path.stem

        documents.append({
            "id": rel_path,
            "content": path.read_text(encoding="utf-8"),
            "metadata": {
                "source": path.name,
                "title": title,
                "doc_type": doc_type,
                "url": None,
            },
        })
    return documents


def chunk_documents(documents: list[dict]) -> list[dict]:
    """
    Chia Document thành chunks có id và chunk_index.
    Dùng RecursiveCharacterTextSplitter để tách theo cấu trúc văn bản.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )

    chunks = []
    for document in documents:
        split_texts = splitter.split_text(document["content"])
        for index, text in enumerate(split_texts):
            if not text.strip():
                continue
            chunks.append({
                "id": f"{document['id']}::chunk-{index}",
                "content": text,
                "metadata": {
                    **document["metadata"],
                    "chunk_index": index,
                },
            })
    return chunks


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """
    Thêm embedding vector vào từng chunk.
    Giữ nguyên các field còn lại của chunk.
    """
    texts = [chunk["content"] for chunk in chunks]
    vectors = embed_texts(texts)
    for chunk, vector in zip(chunks, vectors):
        chunk["embedding"] = vector
    return chunks


def index_to_vectorstore(chunks: list[dict]) -> None:
    """
    Upsert chunks vào ChromaDB.
    Chroma upsert tự động cập nhật nếu ID đã tồn tại → không trùng dữ liệu.
    """
    collection = get_collection()
    collection.upsert(
        ids=[chunk["id"] for chunk in chunks],
        documents=[chunk["content"] for chunk in chunks],
        embeddings=[chunk["embedding"] for chunk in chunks],
        metadatas=[chunk["metadata"] for chunk in chunks],
    )


def run_pipeline() -> None:
    """Chạy load → chunk → embed → index."""
    print("Loading documents...")
    documents = load_documents()
    print(f"  Loaded {len(documents)} documents")

    print("Chunking documents...")
    chunks = chunk_documents(documents)
    print(f"  Created {len(chunks)} chunks")

    print("Embedding chunks...")
    embedded_chunks = embed_chunks(chunks)
    print(f"  Embedded {len(embedded_chunks)} chunks (provider={EMBEDDING_PROVIDER}, dim={EMBEDDING_DIM})")

    print("Indexing to ChromaDB...")
    index_to_vectorstore(embedded_chunks)
    print(f"  Indexed to collection '{COLLECTION_NAME}'")

    collection = get_collection()
    print(f"  Collection count: {collection.count()}")
    print("Done!")


if __name__ == "__main__":
    run_pipeline()
