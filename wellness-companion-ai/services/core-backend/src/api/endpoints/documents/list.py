
# ========================================
# services/core-backend/src/api/endpoints/documents/list.py - UPDATED
# ========================================

"""
Document List API - GET /api/documents/list
Enhanced with proper pagination and filtering
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import logging
import os
import glob
from datetime import datetime

from .pagination import PaginationHelper
from .filtering import DocumentFilter

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/list")
async def list_documents(
    user_id: str = Query(..., description="User ID to list documents for"),
    limit: int = Query(20, ge=1, le=100, description="Number of documents per page"),
    offset: int = Query(0, ge=0, description="Number of documents to skip"),
    file_type: Optional[str] = Query(None, description="Filter by file extension (.pdf, .docx, .txt)"),
    status: Optional[str] = Query(None, description="Filter by status (uploaded, processing, completed)"),
    search: Optional[str] = Query(None, description="Search by filename"),
    sort_by: str = Query("created_at", description="Sort field (created_at, modified_at, filename, size)"),
    sort_order: str = Query("desc", description="Sort order (asc, desc)"),
    start_date: Optional[str] = Query(None, description="Filter by start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="Filter by end date (ISO format)"),
    min_size: Optional[int] = Query(None, description="Minimum file size in bytes"),
    max_size: Optional[int] = Query(None, description="Maximum file size in bytes")
):
    """List user documents with advanced pagination and filtering"""
    
    logger.info(f"Listing documents for user {user_id} with filters")
    
    try:
        # Validate pagination parameters
        pagination_validation = PaginationHelper.validate_pagination_params(limit, offset)
        if not pagination_validation["valid"]:
            raise HTTPException(status_code=400, detail=pagination_validation["errors"])
        
        # Get user upload directory
        user_dir = f"/app/uploads/{user_id}"
        
        if not os.path.exists(user_dir):
            return {
                "documents": [],
                "total": 0,
                "limit": limit,
                "offset": offset,
                "has_more": False,
                "page": 1,
                "total_pages": 1,
                "user_id": user_id,
                "filters_applied": {
                    "file_type": file_type,
                    "status": status,
                    "search": search,
                    "sort_by": sort_by,
                    "sort_order": sort_order
                }
            }
        
        # Get all files in user directory
        all_documents = []
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
                
                document_info = {
                    "document_id": doc_id,
                    "filename": original_name,
                    "file_path": file_path,
                    "size": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "status": "uploaded",  # Default status
                    "file_type": os.path.splitext(original_name)[1].lower()
                }
                
                all_documents.append(document_info)
        
        # Apply filters
        filtered_documents = all_documents
        
        # Filter by file type
        filtered_documents = DocumentFilter.filter_by_file_type(filtered_documents, file_type)
        
        # Filter by status
        filtered_documents = DocumentFilter.filter_by_status(filtered_documents, status)
        
        # Search by filename
        filtered_documents = DocumentFilter.search_by_filename(filtered_documents, search)
        
        # Filter by date range
        filtered_documents = DocumentFilter.filter_by_date_range(filtered_documents, start_date, end_date)
        
        # Filter by size range
        filtered_documents = DocumentFilter.filter_by_size_range(filtered_documents, min_size, max_size)
        
        # Sort documents
        filtered_documents = DocumentFilter.sort_documents(filtered_documents, sort_by, sort_order)
        
        # Apply pagination
        pagination_result = PaginationHelper.paginate_results(filtered_documents, limit, offset)
        
        logger.info(f"Returning {len(pagination_result['items'])} documents out of {pagination_result['total']}")
        
        return {
            "documents": pagination_result["items"],
            "total": pagination_result["total"],
            "limit": pagination_result["limit"],
            "offset": pagination_result["offset"],
            "has_more": pagination_result["has_more"],
            "page": pagination_result["page"],
            "total_pages": pagination_result["total_pages"],
            "user_id": user_id,
            "filters_applied": {
                "file_type": file_type,
                "status": status,
                "search": search,
                "sort_by": sort_by,
                "sort_order": sort_order,
                "date_range": f"{start_date} to {end_date}" if start_date or end_date else None,
                "size_range": f"{min_size}-{max_size} bytes" if min_size or max_size else None
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list documents for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

@router.get("/stats")
async def get_document_stats(user_id: str = Query(...)):
    """Get comprehensive document statistics for user"""
    
    try:
        user_dir = f"/app/uploads/{user_id}"
        
        if not os.path.exists(user_dir):
            return {
                "user_id": user_id,
                "total_documents": 0,
                "total_size": 0,
                "total_size_mb": 0.0,
                "file_types": {},
                "status_breakdown": {},
                "size_distribution": {
                    "small": 0,    # < 1MB
                    "medium": 0,   # 1MB - 10MB
                    "large": 0     # > 10MB
                },
                "recent_uploads": {
                    "today": 0,
                    "this_week": 0,
                    "this_month": 0
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Initialize counters
        total_size = 0
        file_types = {}
        size_distribution = {"small": 0, "medium": 0, "large": 0}
        recent_uploads = {"today": 0, "this_week": 0, "this_month": 0}
        file_count = 0
        
        # Date calculations
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=now.weekday())
        month_start = today_start.replace(day=1)
        
        for file_path in glob.glob(f"{user_dir}/*"):
            if os.path.isfile(file_path):
                filename = os.path.basename(file_path)
                stat = os.stat(file_path)
                size = stat.st_size
                created_at = datetime.fromtimestamp(stat.st_ctime)
                
                # Extract original filename
                if "_" in filename:
                    _, original_name = filename.split("_", 1)
                else:
                    original_name = filename
                
                ext = os.path.splitext(original_name)[1].lower()
                
                # Update counters
                total_size += size
                file_count += 1
                file_types[ext] = file_types.get(ext, 0) + 1
                
                # Size distribution
                if size < 1024 * 1024:  # < 1MB
                    size_distribution["small"] += 1
                elif size < 10 * 1024 * 1024:  # < 10MB
                    size_distribution["medium"] += 1
                else:  # >= 10MB
                    size_distribution["large"] += 1
                
                # Recent uploads
                if created_at >= today_start:
                    recent_uploads["today"] += 1
                if created_at >= week_start:
                    recent_uploads["this_week"] += 1
                if created_at >= month_start:
                    recent_uploads["this_month"] += 1
        
        return {
            "user_id": user_id,
            "total_documents": file_count,
            "total_size": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "total_size_gb": round(total_size / (1024 * 1024 * 1024), 3),
            "file_types": file_types,
            "status_breakdown": {"uploaded": file_count},  # All files are uploaded in this simple implementation
            "size_distribution": size_distribution,
            "recent_uploads": recent_uploads,
            "average_file_size_mb": round((total_size / file_count) / (1024 * 1024), 2) if file_count > 0 else 0,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get stats for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get document stats: {str(e)}")