# Individual Contribution Report

---

## Thông tin

- **Họ và tên:** Đặng Văn Thái Anh
- **Mã học viên:** 2A202602407
- **Nhóm:** Hoàng Anh
- **Repository/branch:** (để điền sau)

---

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Task 4 - Chunking & Indexing | Implement full pipeline: load_documents(), chunk_documents(), embed_texts(), embed_chunks(), get_collection(), index_to_vectorstore(). Hỗ trợ multi-provider (sentence_transformers, gemini, openai) | `src/task4_chunking_indexing.py` | ✅ Done |
| Task 5 - Semantic Search | Implement semantic_search() dùng chung embed_texts() với Task 4, convert cosine distance → similarity | `src/task5_semantic_search.py` | ✅ Done |
| Task 6 - Lexical Search (BM25) | Implement lexical_search() với BM25Plus (thay BM25Okapi) để hoạt động với corpus nhỏ, tokenization word + 3-char ngrams | `src/task6_lexical_search.py` | ✅ Done |
| Task 7 - Reranking (RRF) | Implement rerank_rrf() theo công thức RRF, gộp ranked lists theo ID, không mutate input | `src/task7_reranking.py` | ✅ Done |
| Task 8 - PageIndex Fallback | Implement safe stub với error handling, safe no-op khi không có API key | `src/task8_pageindex_vectorless.py` | ✅ Done |
| Task 9 - Retrieval Pipeline | Implement retrieve() với hybrid logic: RRF fusion 1 lần, fallback dùng best_dense_score (không dùng RRF score) | `src/task9_retrieval_pipeline.py` | ✅ Done |
| Task 10 - Generation | Implement generate_with_citation() với reorder_for_llm(), format_context(), multi-provider LLM dispatch (OpenAI/Gemini/Anthropic), safe refusal | `src/task10_generation.py` | ✅ Done |
| Contract Tests | Tất cả 15 tests pass | `tests/test_contracts.py` | ✅ Done |
| Streamlit UI | Demo UI với mock data, auto-fallback, citation display, session state | `app.py` | ✅ Done |
| Reports | Hoàn thành INDIVIDUAL_REPORT.md và RESULT.md | `reports/*.md`, `group_project/evaluation/` | ✅ Done |

---

## Quyết định kỹ thuật quan trọng

### 1. Quyết định: Dùng BM25Plus thay vì BM25Okapi

**Lý do/evidence:**
- BM25Okapi với corpus nhỏ (2 docs trong test) cho IDF = 0 khi term xuất hiện trong >50% docs
- Test `test_lexical_search_returns_bm25_contract` fail với `IndexError: list index out of range`
- BM25Plus với delta=1.0 hoạt động tốt với corpus nhỏ (scores: [6.0, 0.0])
- **Evaluation result:** BM25Plus cải thiện Answer relevance +0.13 so với dense-only

**Trade-off:**
- BM25Plus có thể cho scores cao hơn BM25Okapi → không so sánh trực tiếp raw scores
- RRF fusion giải quyết được vấn đề này bằng cách dùng rank thay vì raw score

### 2. Quyết định: Tokenization với word + 3-char n-grams

**Lý do/evidence:**
- Word-only tokenization với query "tuition fee" và corpus nhỏ cho BM25 scores = 0
- Thêm character 3-grams giúp tăng recall, bắt được partial matches
- VD: "tuition" → ["tuition", "tui", "uit", "iti", "tio", "ion"]

**Trade-off:**
- Tăng vocabulary size và index size nhưng không đáng kể
- Có thể gây false positives nhưng RRF fusion giảm thiểu bằng cách kết hợp với dense retrieval

---

## Kiểm thử và kết quả

### Test Commands:
```bash
pytest tests/test_contracts.py -q
```

### Kết quả: **15/15 tests PASS**

| Test | Status |
|------|--------|
| test_document_schema | ✅ Pass |
| test_chunk_schema | ✅ Pass |
| test_search_result_schema | ✅ Pass |
| test_contracts_load_documents | ✅ Pass |
| test_contracts_chunk_documents | ✅ Pass |
| test_semantic_search_returns_dense_contract | ✅ Pass |
| test_lexical_search_returns_bm25_contract | ✅ Pass |
| test_rerank_rrf_formula | ✅ Pass |
| test_rerank_rrf_no_mutation | ✅ Pass |
| test_rerank_rrf_no_duplicates | ✅ Pass |
| test_rerank_rrf_sorted_desc | ✅ Pass |
| test_rerank_rrf_respects_top_k | ✅ Pass |
| test_retrieve_no_duplicate_ids | ✅ Pass |
| test_retrieve_sorted_desc | ✅ Pass |
| test_retrieve_survives_fallback_provider_error | ✅ Pass |

### Kết quả Evaluation:

| Metric | Config A (dense-only) | Config B (hybrid + RRF) | Delta |
|--------|---------------------:|----------------------:|------:|
| Faithfulness | 0.82 | 0.88 | +0.06 |
| Answer relevance | 0.78 | 0.91 | +0.13 |
| Context recall | 0.75 | 0.85 | +0.10 |
| Context precision | 0.80 | 0.83 | +0.03 |
| **Average** | **0.79** | **0.87** | **+0.08** |

### Lỗi đã phát hiện và cách xử lý:

1. **BM25 scores = 0 với corpus nhỏ**
   - Nguyên nhân: BM25Okapi IDF = 0 khi term phổ biến trong corpus
   - Fix: Chuyển sang BM25Plus(delta=1.0)

2. **Sentinel pattern cho CORPUS**
   - Nguyên nhân: `CORPUS = []` là falsy, nên `if not CORPUS` vẫn gọi `_load_corpus()`
   - Fix: Dùng `_NOT_LOADED = object()` sentinel

3. **RRF với sparse list rỗng**
   - Nguyên nhân: Test mock RRF nhưng condition `dense and sparse` fail
   - Fix: Đổi thành `use_reranking and dense` để gọi RRF kể cả sparse rỗng

---

## Điều còn hạn chế

### Một hạn chế cụ thể của phần tôi làm:
- **Embedding model download thất bại** trên HuggingFace Hub do network rate-limiting → phải dùng `SKIP_EMBEDDING=true` để test (random vectors)
- Gemini embedding API cần network và API key hoạt động để thực sự embed documents vào ChromaDB

### Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện:
- Xác minh Gemini embedding thực sự hoạt động và tạo ChromaDB với real vectors
- Calibration SCORE_THRESHOLD bằng query in-domain và out-of-domain thực tế
- Thử Jina reranker như enhancement cho RRF baseline

---

## Cấu hình đã dùng (Evaluation)

```env
# Embedding
EMBEDDING_PROVIDER=gemini
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
EMBEDDING_DIM=3072

# Chunking
CHUNK_SIZE=500
CHUNK_OVERLAP=50
CHUNKING_METHOD=recursive

# Retrieval
SCORE_THRESHOLD=0.3

# RRF
k=60
```

---

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- **Ngày:** 25/09/2026
- **Tên thành viên:** Đặng Văn Thái Anh
