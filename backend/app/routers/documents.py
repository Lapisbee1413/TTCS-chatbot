"""
Documents Router - List uploaded documents
"""
import sys
import os
from fastapi import APIRouter, HTTPException
from collections import defaultdict

# Add parent directory to path to import rag_pipeline
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from rag_pipeline import get_collection

from app.models.schemas import DocumentsResponse, DocumentInfo

router = APIRouter()


@router.get("/documents", response_model=DocumentsResponse)
async def list_documents():
    """
    List all uploaded documents in ChromaDB
    
    Returns list of documents with their source names and chunk counts
    """
    try:
        collection = get_collection()
        
        # Get all documents
        all_docs = collection.get()
        
        if not all_docs or not all_docs.get("ids"):
            return DocumentsResponse(
                success=True,
                documents=[],
                total_count=0
            )
        
        # Group by source
        sources = defaultdict(lambda: {"chunks": 0, "articles": set()})
        
        for i, metadata in enumerate(all_docs.get("metadatas", [])):
            source = metadata.get("source", "Unknown")
            article_ref = metadata.get("article_ref", "")
            
            sources[source]["chunks"] += 1
            if article_ref:
                sources[source]["articles"].add(article_ref)
        
        # Format response
        documents = [
            DocumentInfo(
                source=source,
                num_chunks=info["chunks"],
                sample_articles=sorted(list(info["articles"]))[:5]  # First 5 articles
            )
            for source, info in sources.items()
        ]
        
        return DocumentsResponse(
            success=True,
            documents=sorted(documents, key=lambda x: x.source),
            total_count=len(documents)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")
