"""
Document Content Router - Get full document content
"""
import sys
import os
from fastapi import APIRouter, HTTPException
from typing import List, Dict

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from rag_pipeline import get_collection

router = APIRouter()


@router.get("/document/{source_name}/content")
async def get_document_content(source_name: str):
    """
    Get full content of a document by source name
    Returns content grouped by articles
    """
    try:
        collection = get_collection()
        
        # Get all chunks for this source
        results = collection.get(
            where={"source": source_name},
            include=["documents", "metadatas"]
        )
        
        if not results["documents"]:
            raise HTTPException(status_code=404, detail=f"Document '{source_name}' not found")
        
        # Group by article_ref
        articles_dict = {}
        for doc, meta in zip(results["documents"], results["metadatas"]):
            article_ref = meta.get("article_ref", "Không rõ")
            
            if article_ref not in articles_dict:
                articles_dict[article_ref] = []
            
            articles_dict[article_ref].append(doc)
        
        # Format response
        articles = []
        for article_ref in sorted(articles_dict.keys()):
            articles.append({
                "article": article_ref,
                "content": "\n\n".join(articles_dict[article_ref])
            })
        
        return {
            "source": source_name,
            "total_articles": len(articles),
            "articles": articles
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading document: {str(e)}")
