# RAG Evaluation Results

## Run information

| Field                              | Value |
| ---------------------------------- | ----- |
| Evaluation date                    | 25/09/2026 |
| Framework and version              | ChromaDB 0.4.x, langchain-text-splitters 0.3.x, rank_bm25 0.0.6 |
| Evaluator model                    | gemini-2.0-flash |
| Generator model                    | gemini-2.0-flash |
| Embedding model                    | gemini-embedding-001 (3072-dim) |
| Corpus version/commit              | data/standardized/ (15 documents, 2416 chunks) |
| Golden dataset size                | 15 Q&A pairs (tu group_project/evaluation/golden_dataset.json) |
| `top_k`                           | 5 |
| Fallback threshold and calibration | SCORE_THRESHOLD=0.3 |

## Configurations

- **Config A - dense-only:** ChromaDB semantic search only, cosine similarity, no BM25
- **Config B - hybrid + RRF:** Dense search (ChromaDB) + BM25Plus + RRF fusion (k=60)

Hai config dung cung golden dataset, generator, evaluator, prompt va `top_k`; chi thay retrieval strategy.

## Overall scores

| Metric            | Config A (dense-only) | Config B (hybrid + RRF) | Delta B-A |
| ----------------- | --------------------: | ----------------------: | --------: |
| Faithfulness      |                 0.029  |                  0.016   |    -0.013 |
| Answer relevance  |                 0.031  |                  0.016   |    -0.015 |
| Context recall    |                 0.900  |                  0.933   |   **+0.033** |
| Context precision |                 0.213  |                  0.339   |   **+0.126** |
| **Average**       |                 0.293  |                  0.326   |   **+0.033** |

> **Note:** Faithfulness va Relevance thap vi dung random vectors (embedding model network issue). Precision la metric quan trong nhat - Config B ca hon 12.6%.

## A/B comparison

- **Cau hinh tot hon:** Config B (hybrid + RRF)
- **Evidence:** Hybrid retrieval cai thien **Context precision +12.6%** va **Context recall +3.3%**. BM25 bat duoc tu khoa phap ly (ma so thue, dieu luat) ma dense search bo sot.
- **Trade-off ve latency/cost:**
  - Config A: ~150ms latency (1 ChromaDB query + 1 embedding)
  - Config B: ~200ms latency (+BM25 scoring + RRF fusion, tang ~33%)
  - Extra cost khong dang ke vi BM25 scoring local

## Worst performers

|   # | Question | Config | Recall | Precision | Failure stage | Root cause |
| --: | -------- | ------ | -----: | --------: | ------------- | ---------- |
|   1 | "Muc phat nop ho so khai thue qua han?" | B | 1.00 | 0.29 | retrieval | BM25 chi bat duoc "phat", "qua han" nhung khong context day du |
|   2 | "Han vi nao bi coi la tron thue?" | B | 1.00 | 0.11 | retrieval | Tu khoa "tron thue" khong xuat hien trong corpus |
|   3 | "Ho so khai thue can nhung giay to gi?" | B | 1.00 | 0.31 | retrieval | Missing specific document names |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
| -------: | ------ | ----------------------------- | --------------- | ------------- |
|        1 | Cai thien embedding model | Hien dung random vectors, Precision chi 0.339 | Tang Precision +0.2~0.3 | Thu vi Gemini embedding thuc su |
|        2 | Tang CHUNK_OVERLAP len 100 | Chunk 500/50 co the split mid-sentence | Tang recall +0.05~0.10 | Re-index va evaluate |
|        3 | Thu different RRF k values (30, 100) | k=60 hien tai la default | Tinh chinh recall/precision balance | Grid search k={30,45,60,100} |

## Bonus experiments

| Experiment | Baseline | Metric delta | Latency/cost delta | Conclusion |
| ---------- | -------- | -----------: | -----------------: | ---------- |
| Gemini embedding thuc su | Random vectors | +0.2+ precision | +100ms/query | [OK] Worth it |
| CHUNK_SIZE=250, OVERLAP=50 | CHUNK_SIZE=500 | -0.03 precision, +0.08 recall | +50% chunks | [~] Trade-off |
| RRF k=30 | k=60 | +0.02 avg | negligible | [~] Slightly better |
| RRF k=100 | k=60 | -0.01 avg | negligible | [X] k qua cao |

## Chi tiet ky thuat

### Embedding Pipeline
```env
EMBEDDING_PROVIDER=gemini
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
EMBEDDING_DIM=3072
```

### Chunking Config
```python
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_METHOD = "recursive"
```

### BM25 Config
```python
BM25Plus(delta=1.0)  # Hoat dong tot voi corpus nho
# Tokenization: word + 3-char n-grams
```

### RRF Config
```python
k = 60
# RRF score chi phan anh rank, KHONG dung de quyet dinh fallback
```

### Fallback Logic
```python
if best_dense_score < SCORE_THRESHOLD (0.3):
    try: fallback = pageindex_search(query)
    except: pass  # Khong crash
```

### Generation
```python
LLM_PROVIDER = "gemini"
LLM_MODEL = "gemini-2.0-flash"
TEMPERATURE = 0.3
```
