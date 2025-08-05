# ========================================
# services/core-backend/src/api/endpoints/documents/details.py
# ========================================

"""
Document Details API - GET /api/documents/{id}
"""

from fastapi import APIRouter, Path, Query, HTTPException
import logging
import os
import glob
from datetime import datetime
from typing import Optional

from .metadata_formatter import MetadataFormatter

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/{document_id}")
async def get_document_details(
    document_id: str = Path(..., description="Document ID to retrieve"),
    user_id: str = Query(..., description="User ID who owns the document"),
    include_content: bool = Query(False, description="Include file content preview"),
    content_preview_length: int = Query(500, description="Length of content preview in characters")
):
    """Get detailed information about a specific document"""
    
    logger.info(f"Getting details for document {document_id} owned by user {user_id}")
    
    try:
        # Find the document file
        user_dir = f"/app/uploads/{user_id}"
        
        if not os.path.exists(user_dir):
            raise HTTPException(
                status_code=404, 
                detail=f"No documents found for user {user_id}"
            )
        
        # Look for the document by ID
        document_file = None
        for file_path in glob.glob(f"{user_dir}/{document_id}_*"):
            if os.path.isfile(file_path):
                document_file = file_path
                break
        
        if not document_file:
            raise HTTPException(
                status_code=404, 
                detail=f"Document {document_id} not found"
            )
        
        # Extract filename
        filename = os.path.basename(document_file)
        if "_" in filename:
            _, original_name = filename.split("_", 1)
        else:
            original_name = filename
        
        # Get file statistics
        stat = os.stat(document_file)
        
        # Format metadata
        formatter = MetadataFormatter()
        metadata = formatter.format_document_metadata(
            document_id=document_id,
            file_path=document_file,
            original_filename=original_name,
            file_stat=stat
        )
        
        # Get content preview if requested
        content_preview = None
        if include_content:
            try:
                content_preview = formatter.get_content_preview(
                    document_file, 
                    original_name, 
                    content_preview_length
                )
            except Exception as e:
                logger.warning(f"Failed to generate content preview: {e}")
                content_preview = {"error": "Content preview unavailable"}
        
        # Build response
        response = {
            "document_id": document_id,
            "filename": original_name,
            "user_id": user_id,
            "file_path": document_file,
            "status": "uploaded",  # Default status in this simple implementation
            "metadata": metadata,
            "content_preview": content_preview,
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Successfully retrieved details for document {document_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get document details for {document_id}: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve document details: {str(e)}"
        )

@router.get("/{document_id}/metadata")
async def get_document_metadata_only(
    document_id: str = Path(..., description="Document ID"),
    user_id: str = Query(..., description="User ID who owns the document")
):
    """Get only metadata for a specific document (lightweight endpoint)"""
    
    logger.info(f"Getting metadata for document {document_id}")
    
    try:
        user_dir = f"/app/uploads/{user_id}"
        
        if not os.path.exists(user_dir):
            raise HTTPException(status_code=404, detail="User directory not found")
        
        # Find document file
        document_file = None
        for file_path in glob.glob(f"{user_dir}/{document_id}_*"):
            if os.path.isfile(file_path):
                document_file = file_path
                break
        
        if not document_file:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Extract filename
        filename = os.path.basename(document_file)
        if "_" in filename:
            _, original_name = filename.split("_", 1)
        else:
            original_name = filename
        
        # Get file statistics
        stat = os.stat(document_file)
        
        # Format metadata only
        formatter = MetadataFormatter()
        metadata = formatter.format_document_metadata(
            document_id=document_id,
            file_path=document_file,
            original_filename=original_name,
            file_stat=stat
        )
        
        return {
            "document_id": document_id,
            "metadata": metadata,
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get metadata for {document_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{document_id}/content")
async def get_document_content(
    document_id: str = Path(..., description="Document ID"),
    user_id: str = Query(..., description="User ID who owns the document"),
    preview_length: int = Query(1000, description="Content preview length"),
    format: str = Query("text", description="Content format (text, raw)")
):
    """Get document content preview"""
    
    logger.info(f"Getting content for document {document_id}")
    
    try:
        user_dir = f"/app/uploads/{user_id}"
        
        # Find document file
        document_file = None
        for file_path in glob.glob(f"{user_dir}/{document_id}_*"):
            if os.path.isfile(file_path):
                document_file = file_path
                break
        
        if not document_file:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Extract filename
        filename = os.path.basename(document_file)
        if "_" in filename:
            _, original_name = filename.split("_", 1)
        else:
            original_name = filename
        
        # Get content
        formatter = MetadataFormatter()
        content_data = formatter.get_content_preview(
            document_file, 
            original_name, 
            preview_length
        )
        
        return {
            "document_id": document_id,
            "filename": original_name,
            "content_format": format,
            "preview_length": preview_length,
            "content": content_data,
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get content for {document_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
