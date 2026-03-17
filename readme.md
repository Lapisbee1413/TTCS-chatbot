## Cài đặt

### 1. Cài dependencies
```bash
pip install -r requirements.txt
```

### 2. Cài & chạy Ollama (dùng cho RAG Pipeline)
```bash
# Cài Ollama: https://ollama.com
ollama pull qwen2.5:3b
ollama pull mistral
ollama serve          # giữ terminal này chạy nền
```

---

## RAG Pipeline – PDF → ChromaDB → Qwen / Mistral

### Bước 1 – Đọc & nạp file PDF vào ChromaDB
```bash
python ingest.py path/to/document.pdf
# Tuỳ chọn:
python ingest.py doc.pdf --source "Tên tài liệu" --chunk-size 600 --overlap 120
```

### Bước 2 – Đặt câu hỏi (RAG)
```bash
# Dùng Qwen 2.5 (mặc định)
python query.py "Nội dung chính của tài liệu là gì?"

# Dùng Mistral 7B
python query.py "Tóm tắt tài liệu" --model mistral

# Xem chunks ChromaDB tìm được
python query.py "Câu hỏi?" --show-chunks

# Chỉ tìm chunks, không gọi LLM
python query.py "Câu hỏi?" --retrieve-only
```

---

## Kiến trúc RAG

```
PDF/DOCX file
  ↓  pypdf / python-docx (đọc text)
  ↓  chunk_legal_text() – chia theo cấu trúc "Điều X"
  ↓  sentence-transformers – embed từng chunk
  ↓  ChromaDB (lưu persistent tại ./chroma_db/)
      ↓  query bằng embedding của câu hỏi
      ↓  top-K chunks liên quan nhất
  ↓  Ollama (Qwen 2.5:3b hoặc Mistral 7B) – sinh câu trả lời
```
