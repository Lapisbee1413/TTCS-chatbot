"""
Delete Router - Handle document deletion from ChromaDB
"""
import sys
import os
from fastapi import APIRouter, HTTPException

# Add parent directory to path to import rag_pipeline
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from rag_pipeline import get_collection

router = APIRouter()


@router.delete("/documents/{source_name}")
async def delete_document(source_name: str):
    """
    Delete all chunks of a document by source name from ChromaDB
    
    - **source_name**: The source name of the document to delete
    """
    try:
        collection = get_collection()
        
        # Check if source exists
        existing = collection.get(
            where={"source": source_name}
        )
        
        if not existing or not existing["ids"]:
            raise HTTPException(
                status_code=404,
                detail=f"Document with source '{source_name}' not found"
            )
        
        num_chunks = len(existing["ids"])
        
        # Delete all chunks with this source
        collection.delete(
            ids=existing["ids"]
        )
        
        return {
            "success": True,
            "message": f"Deleted {num_chunks} chunks from source '{source_name}'",
            "source_name": source_name,
            "chunks_deleted": num_chunks
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")
