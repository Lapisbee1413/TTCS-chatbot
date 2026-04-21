"""
Query Router - Handle Q&A queries
"""
import sys
import os
from fastapi import APIRouter, HTTPException

# Add parent directory to path to import rag_pipeline
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from rag_pipeline import ask_ollama

from app.models.schemas import QueryRequest, QueryResponse, Citation

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Ask a question and get an answer with citations
    
    - **question**: The question to ask
    - **model**: LLM model to use (default: qwen2.5:3b)
    - **top_k**: Number of chunks to retrieve (default: 5)
    - **source_filter**: Optional filter by source name
    """
    try:
        # Pass source_filter to retrieval stage before generation.
        result = ask_ollama(
            question=request.question,
            model=request.model,
            top_k=request.top_k,
            source_filter=request.source_filter,
            auto_detect_source=request.source_filter is None,
        )
        
        # Extract answer and chunks
        answer = result.get("answer", "Không có câu trả lời.")
        chunks = result.get("chunks_used", [])
        
        if not chunks:
            return QueryResponse(
                success=True,
                answer="Không tìm thấy thông tin liên quan trong cơ sở dữ liệu." if request.source_filter else answer,
                citations=[],
                model_used=request.model,
                chunks_retrieved=0
            )
        
        # Format citations from chunks
        citations = [
            Citation(
                source=chunk.get("metadata", {}).get("source", "Unknown"),
                article_ref=chunk.get("metadata", {}).get("article_ref"),
                chunk_text=chunk.get("text", "")
            )
            for chunk in chunks
        ]
        
        return QueryResponse(
            success=True,
            answer=answer,
            citations=citations,
            model_used=request.model,
            chunks_retrieved=len(chunks)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")
