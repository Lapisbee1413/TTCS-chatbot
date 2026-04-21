"""
Compare Router - Handle version comparison
"""
import sys
import os
from fastapi import APIRouter, HTTPException

# Add parent directory to path to import rag_pipeline
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from rag_pipeline import generate_comparison_report

from app.models.schemas import CompareRequest, CompareResponse

router = APIRouter()


@router.post("/compare", response_model=CompareResponse)
async def compare_versions(request: CompareRequest):
    """
    Compare two versions of the same article
    
    - **article_name**: Name of the article to compare (e.g., "Điều 5")
    - **source_v1**: Source name for version 1
    - **source_v2**: Source name for version 2
    - **model**: LLM model to use (default: qwen2.5:3b)
    """
    try:
        # Generate comparison report using existing RAG pipeline
        result = generate_comparison_report(
            article_name=request.article_name,
            source_v1=request.source_v1,
            source_v2=request.source_v2,
            model=request.model
        )
        
        return CompareResponse(
            success=True,
            article_name=request.article_name,
            v1_source=request.source_v1,
            v2_source=request.source_v2,
            v1_text=result.get("v1_text", ""),
            v2_text=result.get("v2_text", ""),
            comparison_report=result.get("comparison_report", ""),
            citations=result.get("citations", [])
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing documents: {str(e)}")
