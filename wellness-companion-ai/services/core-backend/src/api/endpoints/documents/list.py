
# ========================================
# TASK 41: Document List API - NEW FILES NEEDED
# ========================================

# services/core-backend/src/api/endpoints/documents/list.py
"""
Document List API - GET /api/documents/list
"""

from fastapi import APIRouter, Query
from typing import Optional
import logging
import os
import glob
from datetime import datetime
import json

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/list")
async def list_documents(
    user_id: str = Query(..., description="User ID to list documents for"),
    limit: int = Query(20, ge=1, le=100, description="Number of documents per page"),
    offset: int = Query(0, ge=0, description="Number of documents to skip"),
    file_type: Optional[str] = Query(None, description="Filter by file extension (.pdf, .docx, .txt)")
):
    """List user documents with pagination and filtering"""
    
    logger.info(f"Listing documents for user {user_id}, limit={limit}, offset={offset}")
    
    try:
        # Get user upload directory
        user_dir = f"/app/uploads/{user_id}"
        
        if not os.path.exists(user_dir):
            return {
                "documents": [],
                "total": 0,
                "limit": limit,
                "offset": offset,
                "has_more": False,
                "user_id": user_id
            }
        
        # Get all files in user directory
        all_files = []
        for file_path in glob.glob(f"{user_dir}/*"):
            if os.path.isfile(file_path):
                filename = os.path.basename(file_path)
                
                # Extract document ID and original filename
                if "_" in filename:
                    doc_id, original_name = filename.split("_", 1)
                else:
                    doc_id = filename
                    original_name = filename
                
                # Get file stats
                stat = os.stat(file_path)
                
                # Filter by file type if specified
                if file_type:
                    if not original_name.lower().endswith(file_type.lower()):
                        continue
                
                file_info = {
                    "document_id": doc_id,
                    "filename": original_name,
                    "file_path": file_path,
                    "size": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "status": "uploaded",
                    "file_type": os.path.splitext(original_name)[1].lower()
                }
                
                all_files.append(file_info)
        
        # Sort by created_at (newest first)
        all_files.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Apply pagination
        total = len(all_files)
        paginated_files = all_files[offset:offset + limit]
        
        logger.info(f"Found {total} documents for user {user_id}, returning {len(paginated_files)}")
        
        return {
            "documents": paginated_files,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to list documents for user {user_id}: {e}")
        return {
            "documents": [],
            "total": 0,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/stats")
async def get_document_stats(user_id: str = Query(...)):
    """Get document statistics for user"""
    
    try:
        user_dir = f"/app/uploads/{user_id}"
        
        if not os.path.exists(user_dir):
            return {
                "user_id": user_id,
                "total_documents": 0,
                "total_size": 0,
                "file_types": {},
                "timestamp": datetime.utcnow().isoformat()
            }
        
        total_size = 0
        file_types = {}
        file_count = 0
        
        for file_path in glob.glob(f"{user_dir}/*"):
            if os.path.isfile(file_path):
                filename = os.path.basename(file_path)
                size = os.path.getsize(file_path)
                
                # Extract original filename
                if "_" in filename:
                    _, original_name = filename.split("_", 1)
                else:
                    original_name = filename
                
                ext = os.path.splitext(original_name)[1].lower()
                
                total_size += size
                file_count += 1
                file_types[ext] = file_types.get(ext, 0) + 1
        
        return {
            "user_id": user_id,
            "total_documents": file_count,
            "total_size": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "file_types": file_types,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get stats for user {user_id}: {e}")
        return {"error": str(e)}
