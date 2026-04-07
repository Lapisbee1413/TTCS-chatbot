# 📚 RAG Legal Chatbot

> AI-powered legal document analysis with citation support

**Quick Start:** [Installation](#-quick-start) | [Usage](#-usage) | [Full Docs →](Report/README_FULL.md)

---

## 🚀 Quick Start

```bash
# 1. Install Ollama & models
ollama pull qwen2.5:1.5b
ollama serve

# 2. Install dependencies
pip install -r requirements.txt
cd backend && pip install -r requirements.txt && cd ..
cd frontend && npm install && cd ..

# 3. Start application
start_backend.bat   # Terminal 1
start_frontend.bat  # Terminal 2
```

**Access:**
- 🌐 Frontend: http://localhost:5173
- 🔧 Backend API: http://localhost:8000/docs

---

## ✨ Features

- 📤 **Upload** PDF/DOCX documents
- 💬 **Chat** with citation support
- 🔄 **Compare** document versions
- 📊 **Parallel View** with synchronized scrolling
- 🎯 **Evidence-based** answering

---

## 📁 Project Structure

```
TTCS-chatbot/
├── backend/           # FastAPI REST API
├── frontend/          # React + Material-UI
├── Report/            # 📝 All documentation
│   ├── README_FULL.md
│   ├── USER_GUIDE.md
│   └── PROGRESS_W9.md
├── test_documents/    # 📄 Sample files
├── rag_pipeline.py    # Core RAG logic
└── readme.md          # This file
```

---

## 📖 Documentation

- **[Full Documentation →](Report/README_FULL.md)** - Complete guide
- **[User Guide →](Report/USER_GUIDE.md)** - How to use
- **[Progress Report →](Report/PROGRESS_W9.md)** - Week 9 status

---

## 🛠️ Tech Stack

**Backend:** FastAPI, ChromaDB, Ollama  
**Frontend:** React, Material-UI, Vite  
**Models:** Qwen 2.5, Mistral

---

## 🧪 Testing

```bash
# Backend API tests
cd backend && python test_api.py

# Integration tests
node integration_test.js
```

---

## 📊 Status

✅ **Week 9 Complete** (100%) - Ready for demo!

---

**For detailed information, see [Report/](Report/) folder.**



### Sử dụng compare.py
```bash
# So sánh Điều 5 giữa 2 phiên bản
python compare.py "Điều 5" --v1 "PhuLuc_V1" --v2 "PhuLuc_V2"

# Hiển thị full text + citations
python compare.py "Điều 5" --v1 "HopDong_V1" --v2 "HopDong_V2" --show-full-text --show-citations

# Dùng model Mistral
python compare.py "Điều 3" --v1 "V1" --v2 "V2" --model mistral
```

**Đặc điểm:**
-  Tự động trích dẫn nguồn (citation) cho mọi thông tin
-  Nguyên tắc "Không bằng chứng → Không kết luận"
-  Báo cáo có cấu trúc: Nội dung V1/V2, Điểm giống/khác, Tóm tắt thay đổi
-  Không suy luận hay bổ sung thông tin không có trong văn bản gốc

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
