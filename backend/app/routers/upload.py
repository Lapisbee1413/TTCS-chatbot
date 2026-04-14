"""
Upload Router - Handle document upload with quality validation
"""
import sys
import os
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse

# Add parent directory to path to import rag_pipeline
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from rag_pipeline import ingest_document, read_document
from document_validator import validate_legal_document

from app.models.schemas import UploadResponse

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    source: str = Form(None),
    force: bool = Form(False)
):
    """
    Upload a PDF or DOCX document and ingest it into ChromaDB
    
    - **file**: PDF or DOCX file to upload
    - **source**: Optional source name (defaults to filename without extension)
    - **force**: If true, bypass quality validation (still ingest LOW quality docs)
    """
    try:
        # Validate file type
        if not file.filename.endswith(('.pdf', '.docx', '.PDF', '.DOCX')):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only PDF and DOCX files are supported."
            )
        
        # Create temp directory if not exists
        temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "temp_uploads")
        os.makedirs(temp_dir, exist_ok=True)
        
        # Save uploaded file temporarily
        temp_file_path = os.path.join(temp_dir, file.filename)
        with open(temp_file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Determine source name
        if not source:
            source = os.path.splitext(file.filename)[0]
        
        # Ingest document (includes validation)
        try:
            result = ingest_document(temp_file_path, source_name=source, force=force)
        except ValueError as ve:
            # Validation failed — return quality info with rejection
            # Read the text to get validation details for the response
            raw_text = read_document(temp_file_path)
            validation = validate_legal_document(raw_text)
            os.remove(temp_file_path)
            
            raise HTTPException(
                status_code=422,
                detail={
                    "message": str(ve),
                    "quality": validation["quality"],
                    "score": validation["score"],
                    "checks": [
                        {"name": c["label"], "score": c["score"], "reason": c["reason"]}
                        for c in validation["checks"]
                    ],
                    "hint": "Sử dụng force=true để bỏ qua kiểm tra chất lượng"
                }
            )
        
        # Clean up temp file
        os.remove(temp_file_path)
        
        validation = result.get("validation", {})
        
        return UploadResponse(
            success=True,
            message=f"Document uploaded and processed successfully",
            document_name=file.filename,
            source_name=source,
            num_chunks=result["num_chunks"],
            quality=validation.get("quality", "UNKNOWN"),
            quality_score=validation.get("score", 0),
            quality_summary=validation.get("summary", ""),
            forced=result.get("forced", False),
        )
    
    except HTTPException:
        raise
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

