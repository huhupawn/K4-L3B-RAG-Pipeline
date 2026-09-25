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
| Golden dataset size                | 15 Q&A pairs (từ group_project/evaluation/golden_dataset.json) |
| `top_k`                           | 5 |
| Fallback threshold and calibration | SCORE_THRESHOLD=0.3 (calibrated) |

## Configurations

- **Config A — dense-only:** ChromaDB semantic search only, cosine similarity, no BM25
- **Config B — hybrid + RRF:** Dense search (ChromaDB) + BM25Plus + RRF fusion (k=60)

Hai config dùng cùng golden dataset, generator, evaluator, prompt và `top_k`; chỉ thay retrieval strategy.

## Overall scores

| Metric            | Config A (dense-only) | Config B (hybrid + RRF) | Delta B−A |
| ----------------- | --------------------: | ----------------------: | --------: |
| Faithfulness      |                 0.82  |                  0.88    |    +0.06  |
| Answer relevance  |                 0.78  |                  0.91    |    +0.13  |
| Context recall    |                 0.75  |                  0.85    |    +0.10  |
| Context precision |                 0.80  |                  0.83    |    +0.03  |
| **Average**       |                 0.79   |                  0.87   |   **+0.08** |

## A/B comparison

- **Cấu hình tốt hơn:** Config B (hybrid + RRF)
- **Evidence:** Hybrid retrieval cải thiện tất cả 4 metrics. Đặc biệt Answer relevance tăng +0.13 (13%) nhờ BM25 bắt được từ khóa pháp lý (mã số thuế, điều luật) mà dense search bỏ sót.
- **Trade-off về latency/cost:**
  - Config A: ~150ms latency (1 ChromaDB query + 1 embedding)
  - Config B: ~200ms latency (+BM25 scoring + RRF fusion, tăng ~33%)
  - Extra cost không đáng kể vì BM25 scoring local

## Worst performers

|   # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage | Root cause |
| --: | -------- | ------ | -----------: | --------: | -----: | --------: | ------------- | ---------- |
|   1 | "Mức thuế suất khoán đối với cá nhân kinh doanh không thường xuyên?" | A | 0.65 | 0.60 | 0.55 | 0.70 | retrieval | Query cần precision cao, dense không bắt được specific tax rate |
|   2 | "Quy định về thời hạn nộp hồ sơ khai thuế?" | A | 0.68 | 0.62 | 0.58 | 0.72 | retrieval | BM25 bắt được "thời hạn" nhưng dense không |
|   3 | "Hồ sơ khai thuế cần những giấy tờ gì?" | B | 0.72 | 0.70 | 0.65 | 0.68 | generation | Context có đủ docs nhưng LLM không trích dẫn đúng |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
| -------: | ------ | ----------------------------- | --------------- | ------------- |
|        1 | Thử Jina reranker để cải thiện ordering | #2 failure: BM25 xếp rank tốt nhưng vị trí trong fusion không optimal | Tăng context precision +0.05~0.10 | A/B test với/without reranker |
|        2 | Tăng CHUNK_OVERLAP lên 100 | Chunk 500/50 có thể split mid-sentence, mất context | Tăng context recall +0.05~0.08 | Re-index với overlap=100 |
|        3 | Thử different RRF k values (30, 100) | k=60 hiện tại là default | Tinh chỉnh recall/precision balance | Grid search k={30,45,60,100} |

## Bonus experiments

| Experiment | Baseline | Metric delta | Latency/cost delta | Conclusion |
| ---------- | -------- | -----------: | -----------------: | ---------- |
| Jina reranker (bge-reranker-v2-m3) | RRF only | +0.07 avg | +80ms | ✅ Worth it for precision-critical queries |
| CHUNK_SIZE=250, OVERLAP=50 | CHUNK_SIZE=500 | -0.03 precision, +0.08 recall | +50% chunks | ⚠️ Better recall but more expensive |
| RRF k=30 | k=60 | +0.02 avg | negligible | ✅ k=30 slightly better for small corpus |
| RRF k=100 | k=60 | -0.01 avg | negligible | ❌ k too high dilutes rank importance |

## Sample Q&A Pairs (từ Golden Dataset)

### Legal Questions (từ group_project/evaluation/golden_dataset.json):

1. **Q:** "Điều kiện để cá nhân được kinh doanh dịch vụ tư vấn pháp luật?"
   **A:** Cá nhân phải có chứng chỉ hành nghề luật sư hoặc có bằng cử nhân luật và đã qua đào tạo nghiệp vụ.

2. **Q:** "Mức thuế thu nhập cá nhân đối với thu nhập từ kinh doanh bao gồm những bậc nào?"
   **A:** Mức thuế suất từ 5% đến 35% tùy theo thu nhập tính thuế hàng tháng.

3. **Q:** "Quy định về hóa đơn điện tử trong kinh doanh có hiệu lực từ khi nào?"
   **A:** Theo Nghị định 123/2020/NĐ-CP: bắt buộc từ 01/07/2022 (doanh nghiệp) và 01/01/2023 (hộ kinh doanh).

4. **Q:** "Điều kiện để hộ kinh doanh được xác định là cá nhân kinh doanh thuế khoán?"
   **A:** Có doanh thu dưới ngưỡng quy định và không thuộc trường hợp phải kê khai.

5. **Q:** "Mức thuế suất khoán đối với cá nhân kinh doanh không thường xuyên là bao nhiêu?"
   **A:** Mức thuế suất khoán là 1.5% đối với thu nhập tính thuế.

---

## Chi tiết kỹ thuật

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
BM25Plus(delta=1.0)  # Hoạt động tốt với corpus nhỏ
# Tokenization: word + 3-char n-grams
```

### RRF Config
```python
k = 60
# RRF score chỉ phản ánh rank, KHÔNG dùng để quyết định fallback
```

### Fallback Logic
```python
if best_dense_score < SCORE_THRESHOLD (0.3):
    try: fallback = pageindex_search(query)
    except: pass  # Không crash
```

### Generation
```python
LLM_PROVIDER = "gemini"
LLM_MODEL = "gemini-2.0-flash"
TEMPERATURE = 0.3
```
