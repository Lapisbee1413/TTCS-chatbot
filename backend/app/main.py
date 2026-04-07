"""
FastAPI Backend for RAG Chatbot
Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import upload, query, compare, documents, content

app = FastAPI(
    title="RAG Chatbot API",
    description="Backend API for Legal Document RAG Chatbot with Citation",
    version="1.0.0",
)

# CORS configuration - allow frontend to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default + CRA default
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(query.router, prefix="/api", tags=["query"])
app.include_router(compare.router, prefix="/api", tags=["compare"])
app.include_router(documents.router, prefix="/api", tags=["documents"])
app.include_router(content.router, prefix="/api", tags=["content"])


@app.get("/")
async def root():
    return {
        "message": "RAG Chatbot API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
