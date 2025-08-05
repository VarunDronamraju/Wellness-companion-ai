# ========================================
# services/core-backend/src/api/endpoints/documents/upload.py - SIMPLE VERSION
# ========================================

"""
Document Upload API - POST /api/documents/upload
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
import logging
import os
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

# Simple file validator
def validate_file(filename: str, content_type: str, size: int) -> dict:
    """Simple file validation"""
    
    allowed_extensions = {'.pdf', '.docx', '.txt', '.md'}
    max_size = 50 * 1024 * 1024  # 50MB
    
    if not filename:
        return {"valid": False, "error": "No filename provided"}
    
    ext = os.path.splitext(filename)[1].lower()
    if ext not in allowed_extensions:
        return {"valid": False, "error": f"File type {ext} not allowed"}
    
    if size > max_size:
        return {"valid": False, "error": "File too large (max 50MB)"}
    
    return {"valid": True}

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    title: Optional[str] = Form(None)
):
    """Upload document - simplified version"""
    
    logger.info(f"Upload request: {file.filename} by user {user_id}")
    
    try:
        # Read file content
        content = await file.read()
        
        # Validate file
        validation = validate_file(file.filename, file.content_type, len(content))
        if not validation["valid"]:
            raise HTTPException(status_code=400, detail=validation["error"])
        
        # Generate document ID
        document_id = str(uuid.uuid4())
        
        # Create upload directory
        upload_dir = f"/app/uploads/{user_id}"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = f"{upload_dir}/{document_id}_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(content)
        
        logger.info(f"File saved: {file_path}")
        
        return {
            "success": True,
            "document_id": document_id,
            "filename": file.filename,
            "title": title or file.filename,
            "size": len(content),
            "status": "uploaded",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/status")
async def upload_status():
    """Get upload service status"""
    return {
        "service": "document_upload",
        "status": "operational",
        "supported_formats": [".pdf", ".docx", ".txt", ".md"],
        "max_file_size": "50MB",
        "timestamp": datetime.utcnow().isoformat()
    }