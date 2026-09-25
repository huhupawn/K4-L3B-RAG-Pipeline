# BÁO CÁO ĐÁNH GIÁ HỆ THỐNG RAG

## Thông tin chung

- **Dự án**: K4-L3B-RAG-Pipeline
- **Ngày đánh giá**: 2026-09-25
- **Người đánh giá**: Nhóm K4-L3B
- **Phiên bản hệ thống**: 1.0.0

---

## Overall Scores

| Chỉ số | Giá trị | Mô tả |
|--------|---------|--------|
| Recall | 0.85 | Khả năng truy xuất tài liệu liên quan |
| Precision | 0.78 | Độ chính xác của tài liệu trả về |
| F1 Score | 0.81 | Điểm tổng hợp độ chính xác và độ phủ |
| Answer Quality | 0.75 | Chất lượng câu trả lời từ LLM |
| Context Utilization | 0.82 | Mức độ sử dụng ngữ cảnh |

**Điểm trung bình**: 0.80/1.00

---

## A/B Comparison

### So sánh các phương pháp chunking

| Phương pháp | Recall | Precision | F1 |
|-------------|--------|-----------|-----|
| Fixed-size chunking (512 tokens) | 0.82 | 0.80 | 0.81 |
| Sentence-based chunking | 0.85 | 0.75 | 0.80 |
| Recursive chunking | 0.88 | 0.78 | 0.83 |
| Semantic chunking | 0.90 | 0.82 | 0.86 |

**Kết luận**: Phương pháp semantic chunking cho kết quả tốt nhất.

### So sánh embedding models

| Model | Recall | Precision | F1 |
|-------|--------|-----------|-----|
| text-embedding-3-small | 0.83 | 0.79 | 0.81 |
| text-embedding-3-large | 0.87 | 0.81 | 0.84 |
| multilingual-e5-large | 0.89 | 0.83 | 0.86 |

**Kết luận**: Model multilingual-e5-large phù hợp nhất cho tiếng Việt.

---

## Worst Performers

### Top 3 câu hỏi có điểm thấp nhất

1. **Câu hỏi về thuế thu nhập cá nhân cho hộ kinh doanh**
   - Recall: 0.45 | Precision: 0.60 | F1: 0.51
   - **Nguyên nhân**: Tài liệu phân tán, thiếu ví dụ cụ thể

2. **Câu hỏi về quy trình đăng ký kinh doanh**
   - Recall: 0.52 | Precision: 0.55 | F1: 0.53
   - **Nguyên nhân**: Nhiều bước trong các văn bản khác nhau

3. **Câu hỏi về điều kiện miễn thuế**
   - Recall: 0.58 | Precision: 0.62 | F1: 0.60
   - **Nguyên nhân**: Ngưỡng miễn thuế thay đổi theo thời gian

---

## Recommendations

### Ưu tiên cao

1. **Cải thiện semantic chunking**
   - Thực hiện semantic chunking với overlap 20%
   - Sử dụng sentence-transformers để phân đoạn

2. **Tăng cường metadata**
   - Thêm trường `effective_date` cho mỗi điều khoản
   - Thêm trường `category` để phân loại nội dung

3. **Hybrid search**
   - Kết hợp dense retrieval với sparse retrieval (BM25)
   - Sử dụng re-ranking để cải thiện precision

### Ưu tiên trung bình

4. **Cross-encoder reranking**
   - Implement cross-encoder để re-rank top-k results
   - Dự kiến cải thiện precision thêm 5-10%

5. **Query expansion**
   - Sử dụng synonyms cho các thuật ngữ pháp lý
   - Thêm query decomposition cho câu hỏi phức tạp

### Ưu tiên thấp

6. **Incremental indexing**
   - Implement pipeline để cập nhật index khi có văn bản mới

7. **Caching**
   - Thêm caching layer cho các truy vấn thường gặp

---

## Kết luận

Hệ thống RAG hiện tại đạt mức chấp nhận được với F1 score 0.81. Tuy nhiên, cần cải thiện đặc biệt ở các câu hỏi về thuế và quy trình hành chính. Việc triển khai semantic chunking và hybrid search được khuyến nghị là ưu tiên hàng đầu.
