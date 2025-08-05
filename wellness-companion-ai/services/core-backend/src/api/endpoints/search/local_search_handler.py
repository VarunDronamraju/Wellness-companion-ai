
# ========================================
# services/core-backend/src/api/endpoints/search/local_search_handler.py
# ========================================

"""
Local-only search logic for semantic search
"""

import logging
import os
import glob
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class LocalSearchHandler:
    """Handles local-only search operations"""
    
    def __init__(self):
        self.upload_dir = "/app/uploads"
        self.search_stats = {
            "total_searches": 0,
            "successful_searches": 0,
            "failed_searches": 0,
            "average_results": 0.0
        }
    
    async def get_user_document_count(self, user_id: str) -> int:
        """Get count of documents for user"""
        
        try:
            user_dir = f"{self.upload_dir}/{user_id}"
            if not os.path.exists(user_dir):
                return 0
            
            count = 0
            for file_path in glob.glob(f"{user_dir}/*"):
                if os.path.isfile(file_path):
                    count += 1
            
            return count
            
        except Exception as e:
            logger.error(f"Failed to get document count for user {user_id}: {e}")
            return 0
    
    async def process_search_results(
        self,
        vector_results: Dict[str, Any],
        user_id: str,
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """Process vector search results with local document info"""
        
        try:
            processed_results = []
            
            # Handle case where AI/ML service returns results
            results = vector_results.get("results", [])
            if not results:
                return []
            
            user_dir = f"{self.upload_dir}/{user_id}"
            
            for result in results:
                try:
                    doc_id = result.get("document_id") or result.get("id")
                    if not doc_id:
                        continue
                    
                    # Find document file
                    document_file = None
                    for file_path in glob.glob(f"{user_dir}/{doc_id}_*"):
                        if os.path.isfile(file_path):
                            document_file = file_path
                            break
                    
                    if not document_file:
                        continue
                    
                    # Extract filename
                    filename = os.path.basename(document_file)
                    if "_" in filename:
                        _, original_name = filename.split("_", 1)
                    else:
                        original_name = filename
                    
                    # Get content snippet
                    snippet = await self._get_content_snippet(document_file, original_name)
                    
                    # Build result
                    processed_result = {
                        "document_id": doc_id,
                        "filename": original_name,
                        "score": result.get("score", 0.0),
                        "snippet": snippet
                    }
                    
                    # Add metadata if requested
                    if include_metadata:
                        processed_result["metadata"] = await self._get_document_metadata(document_file)
                    
                    processed_results.append(processed_result)
                    
                except Exception as e:
                    logger.warning(f"Failed to process search result: {e}")
                    continue
            
            # Update stats
            self.search_stats["total_searches"] += 1
            if processed_results:
                self.search_stats["successful_searches"] += 1
                # Update rolling average
                current_avg = self.search_stats["average_results"]
                new_count = len(processed_results)
                total_searches = self.search_stats["successful_searches"]
                self.search_stats["average_results"] = (current_avg * (total_searches - 1) + new_count) / total_searches
            else:
                self.search_stats["failed_searches"] += 1
            
            return processed_results
            
        except Exception as e:
            logger.error(f"Failed to process search results: {e}")
            self.search_stats["failed_searches"] += 1
            return []
    
    async def _get_content_snippet(self, file_path: str, filename: str, max_length: int = 200) -> str:
        """Get content snippet from document"""
        
        try:
            file_ext = os.path.splitext(filename)[1].lower()
            
            if file_ext in ['.txt', '.md']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(max_length * 2)
                    return content[:max_length] + "..." if len(content) > max_length else content
            else:
                return f"[{file_ext.upper()} file - Content preview not available]"
                
        except Exception as e:
            logger.warning(f"Failed to get content snippet: {e}")
            return "[Content preview unavailable]"
    
    async def _get_document_metadata(self, file_path: str) -> Dict[str, Any]:
        """Get basic document metadata"""
        
        try:
            stat = os.stat(file_path)
            return {
                "file_size": stat.st_size,
                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
            }
        except Exception as e:
            logger.warning(f"Failed to get metadata: {e}")
            return {}
    
    async def get_search_stats(self, user_id: str) -> Dict[str, Any]:
        """Get search statistics"""
        
        doc_count = await self.get_user_document_count(user_id)
        
        return {
            "document_count": doc_count,
            "search_statistics": self.search_stats,
            "last_updated": datetime.utcnow().isoformat()
        }