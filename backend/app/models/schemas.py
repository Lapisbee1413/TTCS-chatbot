"""
Pydantic schemas for API request/response models
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


# ──────────────────────────────────────────────
# Upload Models
# ──────────────────────────────────────────────
class UploadResponse(BaseModel):
    success: bool
    message: str
    document_name: str
    source_name: str
    num_chunks: int
    quality: str = "UNKNOWN"
    quality_score: int = 0
    quality_summary: str = ""
    forced: bool = False


# ──────────────────────────────────────────────
# Query Models
# ──────────────────────────────────────────────
class QueryRequest(BaseModel):
    question: str = Field(..., description="User question")
    model: str = Field(default="qwen2.5:3b", description="LLM model to use")
    top_k: int = Field(default=5, description="Number of chunks to retrieve")
    source_filter: Optional[str] = Field(default=None, description="Filter by source name")


class Citation(BaseModel):
    source: str
    article_ref: Optional[str] = None
    chunk_text: str


class QueryResponse(BaseModel):
    success: bool
    answer: str
    citations: List[Citation]
    model_used: str
    chunks_retrieved: int


# ──────────────────────────────────────────────
# Compare Models
# ──────────────────────────────────────────────
class CompareRequest(BaseModel):
    article_name: str = Field(..., description="Article name to compare (e.g., 'Điều 5')")
    source_v1: str = Field(..., description="Source name for version 1")
    source_v2: str = Field(..., description="Source name for version 2")
    model: str = Field(default="qwen2.5:3b", description="LLM model to use")


class CompareResponse(BaseModel):
    success: bool
    article_name: str
    v1_source: str
    v2_source: str
    v1_text: str
    v2_text: str
    comparison_report: str
    citations: List[Dict[str, Any]]


# ──────────────────────────────────────────────
# Documents Models
# ──────────────────────────────────────────────
class DocumentInfo(BaseModel):
    source: str
    num_chunks: int
    sample_articles: List[str]


class DocumentsResponse(BaseModel):
    success: bool
    documents: List[DocumentInfo]
    total_count: int
