
# ========================================
# services/core-backend/src/api/endpoints/documents/cleanup_handler.py
# ========================================

"""
Vector cleanup coordination for document deletion
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class CleanupHandler:
    """Handles cleanup operations when documents are deleted"""
    
    def __init__(self):
        self.cleanup_stats = {
            "total_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0
        }
    
    async def cleanup_document(
        self,
        document_id: str,
        file_path: str,
        user_id: str,
        force: bool = False
    ) -> Dict[str, Any]:
        """Perform comprehensive cleanup for a document"""
        
        logger.info(f"Starting cleanup for document {document_id}")
        
        cleanup_result = {
            "document_id": document_id,
            "user_id": user_id,
            "cleanup_operations": [],
            "overall_success": True,
            "cleanup_time": datetime.utcnow().isoformat()
        }
        
        try:
            # 1. Delete the physical file
            file_cleanup = await self._cleanup_file(file_path)
            cleanup_result["cleanup_operations"].append(file_cleanup)
            
            if not file_cleanup["success"] and not force:
                cleanup_result["overall_success"] = False
                return cleanup_result
            
            # 2. Clean up vector database entries (placeholder for now)
            vector_cleanup = await self._cleanup_vectors(document_id, user_id)
            cleanup_result["cleanup_operations"].append(vector_cleanup)
            
            if not vector_cleanup["success"] and not force:
                cleanup_result["overall_success"] = False
                return cleanup_result
            
            # 3. Clean up metadata entries (placeholder for now)
            metadata_cleanup = await self._cleanup_metadata(document_id, user_id)
            cleanup_result["cleanup_operations"].append(metadata_cleanup)
            
            if not metadata_cleanup["success"] and not force:
                cleanup_result["overall_success"] = False
                return cleanup_result
            
            # 4. Clean up cache entries
            cache_cleanup = await self._cleanup_cache(document_id, user_id)
            cleanup_result["cleanup_operations"].append(cache_cleanup)
            
            # Update stats
            self.cleanup_stats["total_operations"] += 1
            if cleanup_result["overall_success"]:
                self.cleanup_stats["successful_operations"] += 1
            else:
                self.cleanup_stats["failed_operations"] += 1
            
            logger.info(f"Cleanup completed for document {document_id}")
            return cleanup_result
            
        except Exception as e:
            logger.error(f"Cleanup failed for document {document_id}: {e}")
            cleanup_result["overall_success"] = False
            cleanup_result["error"] = str(e)
            self.cleanup_stats["failed_operations"] += 1
            return cleanup_result
    
    async def _cleanup_file(self, file_path: str) -> Dict[str, Any]:
        """Delete the physical file"""
        
        operation = {
            "operation": "file_deletion",
            "file_path": file_path,
            "success": False,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                os.remove(file_path)
                operation.update({
                    "success": True,
                    "file_size": file_size,
                    "message": "File deleted successfully"
                })
                logger.info(f"Deleted file: {file_path}")
            else:
                operation.update({
                    "success": True,  # File already doesn't exist
                    "message": "File already deleted or doesn't exist"
                })
                
        except Exception as e:
            operation.update({
                "success": False,
                "error": str(e),
                "message": f"Failed to delete file: {str(e)}"
            })
            logger.error(f"Failed to delete file {file_path}: {e}")
        
        return operation
    
    async def _cleanup_vectors(self, document_id: str, user_id: str) -> Dict[str, Any]:
        """Clean up vector database entries (placeholder implementation)"""
        
        operation = {
            "operation": "vector_cleanup",
            "document_id": document_id,
            "user_id": user_id,
            "success": True,  # Placeholder - always succeeds for now
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Vector cleanup placeholder - will be implemented in Phase 5"
        }
        
        # TODO: In Phase 5, this will:
        # 1. Connect to Qdrant
        # 2. Find vectors associated with document_id
        # 3. Delete vector entries
        # 4. Return actual cleanup results
        
        logger.info(f"Vector cleanup placeholder for document {document_id}")
        return operation
    
    async def _cleanup_metadata(self, document_id: str, user_id: str) -> Dict[str, Any]:
        """Clean up metadata database entries (placeholder implementation)"""
        
        operation = {
            "operation": "metadata_cleanup",
            "document_id": document_id,
            "user_id": user_id,
            "success": True,  # Placeholder - always succeeds for now
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Metadata cleanup placeholder - will be implemented in Phase 5"
        }
        
        # TODO: In Phase 5, this will:
        # 1. Connect to PostgreSQL
        # 2. Delete document metadata entries
        # 3. Update user statistics
        # 4. Return actual cleanup results
        
        logger.info(f"Metadata cleanup placeholder for document {document_id}")
        return operation
    
    async def _cleanup_cache(self, document_id: str, user_id: str) -> Dict[str, Any]:
        """Clean up cache entries"""
        
        operation = {
            "operation": "cache_cleanup",
            "document_id": document_id,
            "user_id": user_id,
            "success": True,  # Simple implementation - always succeeds
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Cache cleanup completed (file-based cache)"
        }
        
        try:
            # Clear any cached embeddings or processed content
            cache_patterns = [
                f"/app/cache/{user_id}_{document_id}_*",
                f"/app/cache/embeddings_{document_id}_*",
                f"/app/cache/processed_{document_id}_*"
            ]
            
            cleaned_files = 0
            for pattern in cache_patterns:
                import glob
                for cache_file in glob.glob(pattern):
                    try:
                        os.remove(cache_file)
                        cleaned_files += 1
                    except Exception as e:
                        logger.warning(f"Failed to remove cache file {cache_file}: {e}")
            
            operation["cleaned_cache_files"] = cleaned_files
            logger.info(f"Cache cleanup completed for document {document_id}")
            
        except Exception as e:
            operation.update({
                "success": False,
                "error": str(e),
                "message": f"Cache cleanup failed: {str(e)}"
            })
        
        return operation
    
    def get_cleanup_stats(self) -> Dict[str, Any]:
        """Get cleanup operation statistics"""
        
        return {
            "cleanup_stats": self.cleanup_stats,
            "success_rate": (
                self.cleanup_stats["successful_operations"] / 
                max(self.cleanup_stats["total_operations"], 1)
            ) * 100,
            "last_updated": datetime.utcnow().isoformat()
        }