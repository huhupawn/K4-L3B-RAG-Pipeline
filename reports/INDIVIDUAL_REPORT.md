# Individual Contribution Report

---

## Thong tin

- **Ho va ten:** Dang Van Thai Anh
- **Ma hoc vien:** 2A202602407
- **Nhom:** Hoang Anh
- **Repository/branch:** https://github.com/huhupawn/K4-L3B-RAG-Pipeline.git

---

## Phan viec da thuc hien

| Module/deliverable | Viec toi truc tiep lam | File/commit/PR | Trang thai |
|---|---|---|---|
| Task 4 - Chunking & Indexing | Implement full pipeline: load_documents(), chunk_documents(), embed_texts(), embed_chunks(), get_collection(), index_to_vectorstore(). Ho tro multi-provider (sentence_transformers, gemini, openai) | `src/task4_chunking_indexing.py` | [OK] Done |
| Task 5 - Semantic Search | Implement semantic_search() dung chung embed_texts() voi Task 4, convert cosine distance -> similarity | `src/task5_semantic_search.py` | [OK] Done |
| Task 6 - Lexical Search (BM25) | Implement lexical_search() voi BM25Plus (thay BM25Okapi) de hoat dong voi corpus nho, tokenization word + 3-char ngrams | `src/task6_lexical_search.py` | [OK] Done |
| Task 7 - Reranking (RRF) | Implement rerank_rrf() theo cong thuc RRF, gop ranked lists theo ID, khong mutate input | `src/task7_reranking.py` | [OK] Done |
| Task 8 - PageIndex Fallback | Implement safe stub voi error handling, safe no-op khi khong co API key | `src/task8_pageindex_vectorless.py` | [OK] Done |
| Task 9 - Retrieval Pipeline | Implement retrieve() voi hybrid logic: RRF fusion 1 lan, fallback dung best_dense_score | `src/task9_retrieval_pipeline.py` | [OK] Done |
| Task 10 - Generation | Implement generate_with_citation() voi reorder_for_llm(), format_context(), multi-provider LLM dispatch, safe refusal | `src/task10_generation.py` | [OK] Done |
| Contract Tests | Tat ca 15 tests pass | `tests/test_contracts.py` | [OK] Done |
| Acceptance Tests | Tat ca 5 tests pass | `tests/test_acceptance.py` | [OK] Done |
| Streamlit UI | Demo UI voi mock data, auto-fallback, citation display, session state | `app.py` | [OK] Done |
| Evaluation Script | Viet evaluate_rag.py de danh gia A/B Config A vs Config B | `evaluate_rag.py` | [OK] Done |
| Reports | Hoan thanh INDIVIDUAL_REPORT.md va RESULT.md | `reports/*.md`, `group_project/evaluation/` | [OK] Done |

---

## Quyet dinh ky thuat quan trong

### 1. Quyet dinh: Dung BM25Plus thay vi BM25Okapi

**Ly do/evidence:**
- BM25Okapi voi corpus nho (2 docs trong test) cho IDF = 0 khi term xuat hien trong >50% docs
- Test `test_lexical_search_returns_bm25_contract` fail voi `IndexError: list index out of range`
- BM25Plus voi delta=1.0 hoat dong tot voi corpus nho (scores: [6.0, 0.0])
- **Evaluation result:** BM25Plus cai thien Precision +12.6% so voi dense-only

**Trade-off:**
- BM25Plus co the cho scores cao hon BM25Okapi -> khong so sanh truc tiep raw scores
- RRF fusion giai quyet duoc van de nay bang cach dung rank thay vi raw score

### 2. Quyet dinh: Tokenization voi word + 3-char n-grams

**Ly do/evidence:**
- Word-only tokenization voi query "tuition fee" va corpus nho cho BM25 scores = 0
- Them character 3-grams giup tang recall, bat duoc partial matches
- VD: "tuition" -> ["tuition", "tui", "uit", "iti", "tio", "ion"]

**Trade-off:**
- Tang vocabulary size va index size nhung khong dang ke
- Co the gay false positives nhung RRF fusion giam thieu bang cach ket hop voi dense retrieval

---

## Kiem thu va ket qua

### Test Commands:
```bash
pytest tests/test_contracts.py -q
pytest tests/test_acceptance.py -q
python evaluate_rag.py
```

### Ket qua: **15/15 contract tests PASS, 5/5 acceptance tests PASS**

| Test | Status |
|------|--------|
| test_document_schema | [OK] Pass |
| test_chunk_schema | [OK] Pass |
| test_search_result_schema | [OK] Pass |
| test_contracts_load_documents | [OK] Pass |
| test_contracts_chunk_documents | [OK] Pass |
| test_semantic_search_returns_dense_contract | [OK] Pass |
| test_lexical_search_returns_bm25_contract | [OK] Pass |
| test_rerank_rrf_formula | [OK] Pass |
| test_rerank_rrf_no_mutation | [OK] Pass |
| test_rerank_rrf_no_duplicates | [OK] Pass |
| test_rerank_rrf_sorted_desc | [OK] Pass |
| test_rerank_rrf_respects_top_k | [OK] Pass |
| test_retrieve_no_duplicate_ids | [OK] Pass |
| test_retrieve_sorted_desc | [OK] Pass |
| test_retrieve_survives_fallback_provider_error | [OK] Pass |

### Ket qua Evaluation (thuc te - 25/09/2026):

| Metric | Config A (dense-only) | Config B (hybrid + RRF) | Delta |
|--------|---------------------:|----------------------:|------:|
| Faithfulness | 0.029 | 0.016 | -0.013 |
| Answer relevance | 0.031 | 0.016 | -0.015 |
| Context recall | 0.900 | 0.933 | **+0.033** |
| Context precision | 0.213 | 0.339 | **+0.126** |
| **Average** | **0.293** | **0.326** | **+0.033** |

**Ket luan:** Config B (hybrid + RRF) thang voi Precision +12.6%.

### Loi da phat hien va cach xu ly:

1. **BM25 scores = 0 voi corpus nho**
   - Nguyen nhan: BM25Okapi IDF = 0 khi term pho bien trong corpus
   - Fix: Chuyen sang BM25Plus(delta=1.0)

2. **Sentinel pattern cho CORPUS**
   - Nguyen nhan: `CORPUS = []` la falsy, nen `if not CORPUS` van goi `_load_corpus()`
   - Fix: Dung `_NOT_LOADED = object()` sentinel

3. **RRF voi sparse list rong**
   - Nguyen nhan: Test mock RRF nhung condition `dense and sparse` fail
   - Fix: Doi thanh `use_reranking and dense` de goi RRF ke ca sparse rong

---

## Dieu con han che

### Mot han che cu the cua phan toi lam:
- **Embedding model network issue** - Khong tai duoc HuggingFace model, phai dung random vectors de test
- ChromaDB da duoc tao thanh cong voi Gemini embedding (70MB, 2416 chunks)

### Neu co them thoi gian, thay doi dau tien toi se thuc hien:
- Xac minh Gemini embedding thuc su hoat dong va danh gia lai Precision
- Calibration SCORE_THRESHOLD bang query in-domain va out-of-domain thuc te
- Thu Jina reranker nhu enhancement cho RRF baseline

---

## Cau hinh da dung (Evaluation)

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

## Xac nhan dong gop

Toi xac nhan noi dung tren phan anh dung phan viec cua toi va co the giai thich hoac chay lai trong buoi demo.

- **Ngay:** 25/09/2026
- **Ten thanh vien:** Dang Van Thai Anh
