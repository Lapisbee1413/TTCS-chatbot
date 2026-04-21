# 📚 RAG Legal Document Chatbot

AI-powered chatbot for legal document analysis with citation support. Upload documents, ask questions, and compare versions with evidence-based answers.

**Project Status:** Week 9 - UI Development ✅ (85% Complete)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Ollama (for LLM models)

### 1. Install Ollama & Pull Models
```bash
# Install from: https://ollama.com
ollama pull qwen2.5:3b
ollama pull mistral
ollama serve  # Keep this running
```

### 2. Install Backend Dependencies
```bash
pip install -r requirements.txt
cd backend
pip install -r requirements.txt
```

### 3. Install Frontend Dependencies
```bash
cd frontend
npm install
```

### 4. Start the Application

**Option A: Using Batch Files (Windows)**
```bash
# Terminal 1: Backend
start_backend.bat

# Terminal 2: Frontend
start_frontend.bat
```

**Option B: Manual Start**
```bash
# Terminal 1: Backend API
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

**Access:**
- 🌐 Frontend UI: http://localhost:5173
- 🔧 Backend API: http://localhost:8000
- 📖 API Docs: http://localhost:8000/docs

---

## 📋 Features

### ✅ Week 1-8 (Completed)
- [x] RAG Pipeline (PDF/DOCX → ChromaDB → LLM)
- [x] Legal document chunking (by "Điều X")
- [x] Citation system with evidence-based answering
- [x] Version comparison with detailed reports
- [x] CLI tools (ingest.py, query.py, compare.py)

### ✅ Week 9 (Current - 85% Complete)
- [x] **Backend API (FastAPI)**
  - Upload documents
  - Query/Chat endpoint
  - Compare versions
  - List documents
- [x] **Frontend UI (React + Material-UI)**
  - Upload page with validation
  - Chat interface with citations
  - Parallel view (side-by-side)
  - Compare page with detailed reports
  - Responsive layout

### ⏳ Remaining Tasks
- [ ] Synchronized scrolling for parallel view
- [ ] Difference highlighting
- [ ] UI polish & accessibility
- [ ] Full documentation with screenshots

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│    React Frontend (Port 5173)           │
│  - Material-UI                          │
│  - React Router                         │
│  - Axios HTTP Client                    │
└────────────────┬────────────────────────┘
                 │ HTTP REST API
┌────────────────▼────────────────────────┐
│   FastAPI Backend (Port 8000)           │
│  - CORS enabled                         │
│  - Pydantic validation                  │
│  - 4 REST endpoints                     │
└────────────────┬────────────────────────┘
                 │ Function calls
┌────────────────▼────────────────────────┐
│     RAG Pipeline (Python)               │
│  - ingest_document()                    │
│  - ask_ollama()                         │
│  - generate_comparison_report()         │
│  - retrieve()                           │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│  ChromaDB + Ollama                      │
│  - sentence-transformers embedding      │
│  - Qwen 2.5:3b / Mistral 7B            │
└─────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
TTCS-chatbot/
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── main.py          # FastAPI app entry
│   │   ├── models/          # Pydantic schemas
│   │   └── routers/         # API endpoints
│   ├── requirements.txt
│   ├── test_api.py          # API tests
│   └── README.md
│
├── frontend/                # React frontend
│   ├── src/
│   │   ├── api/            # API client
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── App.jsx         # Main app + routing
│   │   └── config.js       # Configuration
│   ├── package.json
│   └── vite.config.js
│
├── rag_pipeline.py          # Core RAG logic
├── ingest.py                # CLI: Upload documents
├── query.py                 # CLI: Ask questions
├── compare.py               # CLI: Compare versions
├── requirements.txt         # Python dependencies
├── start_backend.bat        # Start backend
├── start_frontend.bat       # Start frontend
├── PROGRESS_W9.md          # Week 9 progress
└── readme.md               # This file
```

---

## 🔧 CLI Tools (Weeks 1-8)

### Upload Document
```bash
python ingest.py hopdong_v1.docx --source "HopDong_V1"
python ingest.py phuluc_v2.pdf --source "PhuLuc_V2"
```

### Query Documents
```bash
python query.py "Điều 5 quy định gì?"
python query.py "Nội dung chính?" --model mistral --show-chunks
python query.py "Câu hỏi?" --retrieve-only
```

### Compare Versions
```bash
python compare.py "Điều 5" --v1 "HopDong_V1" --v2 "HopDong_V2"
python compare.py "Điều 3" --show-full-text --show-citations
```

---

## 🌐 Web UI (Week 9)

### 1. Upload Page
- Drag & drop or browse files
- Support PDF & DOCX
- File validation (type, size)
- Custom source naming

### 2. Chat Page
- Real-time Q&A
- Citation display (chips)
- Chat history
- Evidence-based answers

### 3. Parallel View
- Side-by-side document comparison
- Version selector
- (Coming: sync scroll & highlighting)

### 4. Compare Page
- Select article to compare
- Choose 2 versions
- Detailed comparison report
- Side-by-side content view

---

## 🧪 Testing

### Backend API
```bash
cd backend
python test_api.py
```

### Manual Testing
1. Start backend + frontend
2. Upload a document via UI
3. Test chat functionality
4. Try comparing versions

---

## 🔐 API Endpoints

### POST /api/upload
Upload a document (PDF/DOCX)
```json
FormData {
  "file": File,
  "source": "HopDong_V1"  // optional
}
```

### POST /api/query
Ask a question
```json
{
  "question": "Điều 5 quy định gì?",
  "model": "qwen2.5:3b",
  "top_k": 5,
  "source_filter": null
}
```

### POST /api/compare
Compare two versions
```json
{
  "article_name": "Điều 5",
  "source_v1": "HopDong_V1",
  "source_v2": "HopDong_V2",
  "model": "qwen2.5:3b"
}
```

### GET /api/documents
List all uploaded documents

---

## 🛠️ Tech Stack

**Backend:**
- FastAPI 0.135.3
- ChromaDB (vector database)
- sentence-transformers (embeddings)
- Ollama (LLM inference)
- Python 3.8+

**Frontend:**
- React 18
- Vite (build tool)
- Material-UI v5
- React Router v6
- Axios

**Models:**
- Qwen 2.5:3b (default LLM)
- Mistral 7B (alternative)
- paraphrase-multilingual-MiniLM-L12-v2 (embeddings)

---

## 📊 Progress Tracking

| Week | Task | Status |
|------|------|--------|
| W1-2 | Model selection | ✅ 100% |
| W3-4 | Data ingestion & chunking | ✅ 100% |
| W5-6 | Index & retrieval | ✅ 100% |
| W7-8 | Citation & comparison | ✅ 100% |
| **W9** | **UI Development** | **✅ 85%** |
| W10 | Dataset & evaluation | ✅ Baseline + Round2 |
| W11 | Quality improvement | ✅ Round2 + comparison report |
| W12 | Final report & demo | ⏳ Pending |

---

## 📝 Notes

- **Evidence-Based Principle:** LLM follows "Không bằng chứng → Không kết luận"
- **Citation System:** Every answer includes `[Nguồn: X, Điều Y]`
- **Chunking Strategy:** Legal-pattern-based (by "Điều X") + size-based fallback
- **CORS:** Enabled for localhost:5173 and localhost:3000

---

## 👥 Team

OOP Project - TTCS Chatbot
Deadline Week 9: April 7, 2026

---

## 📄 License

Educational project for OOP course.
