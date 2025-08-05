
# ========================================
# services/core-backend/src/services/document_service.py
# ========================================

"""
Document Service - Business logic for document management
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class DocumentService:
    """Service for document management operations"""
    
    def __init__(self):
        # In-memory storage for now (will be replaced with database in Phase 5)
        self._documents = {}
        logger.info("Document service initialized")
    
    async def create_document(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new document record"""
        
        try:
            # Generate document ID
            document_id = str(uuid.uuid4())
            
            # Create document record
            document = {
                "id": document_id,
                "user_id": document_data["user_id"],
                "filename": document_data["filename"],
                "title": document_data.get("title", document_data["filename"]),
                "description": document_data.get("description", ""),
                "file_path": document_data["file_path"],
                "file_size": document_data["file_size"],
                "mime_type": document_data.get("mime_type"),
                "status": document_data.get("status", "uploaded"),
                "processing_id": None,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "metadata": {}
            }
            
            # Store document
            self._documents[document_id] = document
            
            logger.info(f"Document created: {document_id} - {document['filename']}")
            return document
            
        except Exception as e:
            logger.error(f"Failed to create document: {e}")
            raise Exception(f"Document creation failed: {str(e)}")
    
    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID"""
        
        try:
            document = self._documents.get(document_id)
            if document:
                logger.debug(f"Retrieved document: {document_id}")
            else:
                logger.warning(f"Document not found: {document_id}")
            
            return document
            
        except Exception as e:
            logger.error(f"Failed to get document {document_id}: {e}")
            return None
    
    async def update_document_status(
        self, 
        document_id: str, 
        status: str, 
        processing_id: Optional[str] = None
    ) -> bool:
        """Update document status"""
        
        try:
            if document_id not in self._documents:
                logger.warning(f"Cannot update status - document not found: {document_id}")
                return False
            
            # Update document
            self._documents[document_id]["status"] = status
            self._documents[document_id]["updated_at"] = datetime.utcnow().isoformat()
            
            if processing_id:
                self._documents[document_id]["processing_id"] = processing_id
            
            logger.info(f"Document status updated: {document_id} -> {status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update document status {document_id}: {e}")
            return False
    
    async def list_documents(
        self, 
        user_id: str, 
        limit: int = 50, 
        offset: int = 0
    ) -> Dict[str, Any]:
        """List user documents with pagination"""
        
        try:
            # Filter documents by user_id
            user_documents = [
                doc for doc in self._documents.values() 
                if doc["user_id"] == user_id
            ]
            
            # Sort by created_at (newest first)
            user_documents.sort(key=lambda x: x["created_at"], reverse=True)
            
            # Apply pagination
            paginated_docs = user_documents[offset:offset + limit]
            
            logger.info(f"Retrieved {len(paginated_docs)} documents for user {user_id}")
            
            return {
                "documents": paginated_docs,
                "total": len(user_documents),
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < len(user_documents)
            }
            
        except Exception as e:
            logger.error(f"Failed to list documents for user {user_id}: {e}")
            return {"documents": [], "total": 0, "limit": limit, "offset": offset}
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete document record"""
        
        try:
            if document_id in self._documents:
                deleted_doc = self._documents.pop(document_id)
                logger.info(f"Document deleted: {document_id} - {deleted_doc['filename']}")
                return True
            else:
                logger.warning(f"Cannot delete - document not found: {document_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {e}")
            return False
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get document service statistics"""
        
        try:
            total_docs = len(self._documents)
            status_counts = {}
            
            for doc in self._documents.values():
                status = doc["status"]
                status_counts[status] = status_counts.get(status, 0) + 1
            
            return {
                "total_documents": total_docs,
                "status_breakdown": status_counts,
                "service": "document_service",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get service stats: {e}")
            return {"error": str(e)}