# ========================================
# services/core-backend/src/api/endpoints/documents/delete.py
# ========================================

"""
Document Delete API - DELETE /api/documents/{id}
"""

from fastapi import APIRouter, Path, Query, HTTPException
import logging
import os
import glob
from datetime import datetime
from typing import Dict, Any

from .cleanup_handler import CleanupHandler

logger = logging.getLogger(__name__)
router = APIRouter()

@router.delete("/{document_id}")
async def delete_document(
    document_id: str = Path(..., description="Document ID to delete"),
    user_id: str = Query(..., description="User ID who owns the document"),
    force: bool = Query(False, description="Force delete even if cleanup fails")
):
    """Delete a document and clean up associated resources"""
    
    logger.info(f"Delete request for document {document_id} by user {user_id}")
    
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
        
        # Get file info before deletion
        filename = os.path.basename(document_file)
        if "_" in filename:
            _, original_name = filename.split("_", 1)
        else:
            original_name = filename
        
        file_size = os.path.getsize(document_file)
        
        # Initialize cleanup handler
        cleanup_handler = CleanupHandler()
        
        # Perform cleanup operations
        cleanup_result = await cleanup_handler.cleanup_document(
            document_id=document_id,
            file_path=document_file,
            user_id=user_id,
            force=force
        )
        
        logger.info(f"Document {document_id} deleted successfully")
        
        return {
            "success": True,
            "document_id": document_id,
            "filename": original_name,
            "file_size": file_size,
            "user_id": user_id,
            "cleanup_result": cleanup_result,
            "deleted_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document {document_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete document: {str(e)}"
        )

@router.delete("/batch")
async def delete_multiple_documents(
    user_id: str = Query(..., description="User ID who owns the documents"),
    document_ids: str = Query(..., description="Comma-separated list of document IDs"),
    force: bool = Query(False, description="Force delete even if some cleanups fail")
):
    """Delete multiple documents in batch"""
    
    logger.info(f"Batch delete request for user {user_id}")
    
    try:
        # Parse document IDs
        doc_ids = [doc_id.strip() for doc_id in document_ids.split(",") if doc_id.strip()]
        
        if not doc_ids:
            raise HTTPException(status_code=400, detail="No document IDs provided")
        
        if len(doc_ids) > 50:  # Limit batch size
            raise HTTPException(status_code=400, detail="Too many documents (max 50)")
        
        # Initialize cleanup handler
        cleanup_handler = CleanupHandler()
        
        # Process each document
        results = []
        successful_deletions = 0
        failed_deletions = 0
        
        for doc_id in doc_ids:
            try:
                # Find document file
                user_dir = f"/app/uploads/{user_id}"
                document_file = None
                
                for file_path in glob.glob(f"{user_dir}/{doc_id}_*"):
                    if os.path.isfile(file_path):
                        document_file = file_path
                        break
                
                if not document_file:
                    results.append({
                        "document_id": doc_id,
                        "success": False,
                        "error": "Document not found"
                    })
                    failed_deletions += 1
                    continue
                
                # Get file info
                filename = os.path.basename(document_file)
                if "_" in filename:
                    _, original_name = filename.split("_", 1)
                else:
                    original_name = filename
                
                file_size = os.path.getsize(document_file)
                
                # Perform cleanup
                cleanup_result = await cleanup_handler.cleanup_document(
                    document_id=doc_id,
                    file_path=document_file,
                    user_id=user_id,
                    force=force
                )
                
                results.append({
                    "document_id": doc_id,
                    "success": True,
                    "filename": original_name,
                    "file_size": file_size,
                    "cleanup_result": cleanup_result
                })
                successful_deletions += 1
                
            except Exception as e:
                logger.error(f"Failed to delete document {doc_id}: {e}")
                results.append({
                    "document_id": doc_id,
                    "success": False,
                    "error": str(e)
                })
                failed_deletions += 1
        
        return {
            "batch_delete": True,
            "total_requested": len(doc_ids),
            "successful_deletions": successful_deletions,
            "failed_deletions": failed_deletions,
            "results": results,
            "user_id": user_id,
            "deleted_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch delete failed for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Batch delete failed: {str(e)}")

@router.delete("/user/{user_id}/all")
async def delete_all_user_documents(
    user_id: str = Path(..., description="User ID"),
    confirm: str = Query(..., description="Must be 'DELETE_ALL' to confirm"),
    force: bool = Query(False, description="Force delete even if cleanups fail")
):
    """Delete all documents for a user (dangerous operation)"""
    
    if confirm != "DELETE_ALL":
        raise HTTPException(
            status_code=400,
            detail="Must provide confirm='DELETE_ALL' to proceed"
        )
    
    logger.warning(f"DELETE ALL documents request for user {user_id}")
    
    try:
        user_dir = f"/app/uploads/{user_id}"
        
        if not os.path.exists(user_dir):
            return {
                "success": True,
                "message": "No documents found to delete",
                "user_id": user_id,
                "deleted_count": 0
            }
        
        # Get all documents
        all_files = []
        for file_path in glob.glob(f"{user_dir}/*"):
            if os.path.isfile(file_path):
                all_files.append(file_path)
        
        if not all_files:
            return {
                "success": True,
                "message": "No documents found to delete",
                "user_id": user_id,
                "deleted_count": 0
            }
        
        # Initialize cleanup handler
        cleanup_handler = CleanupHandler()
        
        # Delete all documents
        deleted_count = 0
        total_size = 0
        
        for file_path in all_files:
            try:
                filename = os.path.basename(file_path)
                if "_" in filename:
                    doc_id, _ = filename.split("_", 1)
                else:
                    doc_id = filename
                
                file_size = os.path.getsize(file_path)
                total_size += file_size
                
                await cleanup_handler.cleanup_document(
                    document_id=doc_id,
                    file_path=file_path,
                    user_id=user_id,
                    force=force
                )
                
                deleted_count += 1
                
            except Exception as e:
                logger.error(f"Failed to delete file {file_path}: {e}")
                if not force:
                    raise
        
        # Remove user directory if empty
        try:
            remaining_files = os.listdir(user_dir)
            if not remaining_files:
                os.rmdir(user_dir)
                logger.info(f"Removed empty user directory: {user_dir}")
        except Exception as e:
            logger.warning(f"Failed to remove user directory: {e}")
        
        logger.warning(f"Deleted ALL {deleted_count} documents for user {user_id}")
        
        return {
            "success": True,
            "message": f"Deleted all documents for user {user_id}",
            "user_id": user_id,
            "deleted_count": deleted_count,
            "total_size_deleted": total_size,
            "deleted_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete all documents for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete all documents: {str(e)}"
        )
