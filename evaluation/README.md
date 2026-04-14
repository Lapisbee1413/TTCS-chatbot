# Evaluation Module

## Mô tả

Module đánh giá chất lượng RAG chatbot. Bao gồm:
- **qa_dataset.json** — 45 câu hỏi Q&A với ground truth (5 loại)
- **compare_dataset.json** — 12 cặp so sánh với expected changes
- **metrics.py** — 5 metrics đánh giá
- **evaluate.py** — Script chạy đánh giá tự động
- **baseline_results.json** — Kết quả baseline (auto-generated)

## Cách chạy

### Yêu cầu
1. Ollama đang chạy: `ollama serve`
2. Đã ingest tài liệu test vào ChromaDB

### Ingest tài liệu test (nếu chưa)
```bash
python ingest.py test_documents/hopdong_thue_nha_v1.docx --source ThueNha_V1
python ingest.py test_documents/hopdong_thue_nha_v2.docx --source ThueNha_V2
python ingest.py test_documents/hopdong_dichvu_baotri.docx --source DichVu_BaoTri
python ingest.py test_documents/hopdong_laodong.docx --source LaoDong
python ingest.py test_documents/hopdong_muaban_thietbi.docx --source MuaBan_ThietBi
python ingest.py test_documents/hopdong_v1.docx --source HopDong_V1
python ingest.py test_documents/hopdong_v2.docx --source HopDong_V2
python ingest.py test_documents/phuluc_kho_v1.docx --source PhuLuc_V1
python ingest.py test_documents/phuluc_kho_v2.docx --source PhuLuc_V2
```

### Chạy đánh giá
```bash
# Đánh giá đầy đủ (Q&A + Compare)
python evaluation/evaluate.py

# Chỉ Q&A
python evaluation/evaluate.py --qa-only

# Chỉ Compare
python evaluation/evaluate.py --compare-only

# Dùng model khác
python evaluation/evaluate.py --model mistral
```

## Metrics

| Metric | Mô tả | Range |
|--------|--------|-------|
| Retrieval Accuracy | Chunks truy vấn có đúng article? | 0.0 - 1.0 |
| Answer Relevance | Câu trả lời có chứa keywords mong đợi? | 0.0 - 1.0 |
| Citation Accuracy | Citations có đúng source + article? | 0.0 - 1.0 |
| Hallucination Rate | Chatbot có bịa khi không biết? | 0.0 - 1.0 (thấp = tốt) |
| Compare Completeness | Phát hiện đủ thay đổi? | 0.0 - 1.0 |

## Phân loại câu hỏi

| Loại | Số lượng | Mô tả |
|------|:--------:|-------|
| factual | 18 | Hỏi thông tin cụ thể trong 1 điều khoản |
| multi_article | 5 | Cần kết hợp nhiều điều khoản |
| cross_document | 4 | Hỏi về nhiều tài liệu |
| unanswerable | 8 | Câu hỏi không có trong tài liệu |
| comparison | 7+3 | So sánh 2 phiên bản |
