# FastAPI Backend - RAG Chatbot

Backend API cho Legal Document RAG Chatbot với Citation.

## Cài đặt

```bash
cd backend
pip install -r requirements.txt
```

## Chạy Server

```bash
# Development mode với auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Server sẽ chạy tại: `http://localhost:8000`

## API Documentation

Swagger UI: `http://localhost:8000/docs`
ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### 1. Upload Document
```http
POST /api/upload
Content-Type: multipart/form-data

file: (PDF/DOCX file)
source: (optional) source name
```

### 2. Query/Chat
```http
POST /api/query
Content-Type: application/json

{
  "question": "Điều 5 quy định gì?",
  "model": "qwen2.5:3b",
  "top_k": 5,
  "source_filter": "HopDong_V1"
}
```

### 3. Compare Versions
```http
POST /api/compare
Content-Type: application/json

{
  "article_name": "Điều 5",
  "source_v1": "HopDong_V1",
  "source_v2": "HopDong_V2",
  "model": "qwen2.5:3b"
}
```

### 4. List Documents
```http
GET /api/documents
```

## Kiến trúc

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py       # Pydantic models
│   └── routers/
│       ├── __init__.py
│       ├── upload.py        # Upload endpoint
│       ├── query.py         # Query endpoint
│       ├── compare.py       # Compare endpoint
│       └── documents.py     # List docs endpoint
└── requirements.txt
```

## Test với curl

```bash
# Health check
curl http://localhost:8000/health

# Upload document
curl -X POST http://localhost:8000/api/upload \
  -F "file=@../hopdong_v1.docx" \
  -F "source=HopDong_V1"

# Query
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Điều 2 quy định gì?", "top_k": 3}'

# Compare
curl -X POST http://localhost:8000/api/compare \
  -H "Content-Type: application/json" \
  -d '{"article_name": "Điều 2", "source_v1": "HopDong_V1", "source_v2": "HopDong_V2"}'

# List documents
curl http://localhost:8000/api/documents
```
