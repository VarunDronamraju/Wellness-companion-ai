
# File 3: services/data-layer/src/embedding_pipeline/processing_status.py
"""
Track and manage document processing status and progress.
"""

import logging
from typing import Dict, Any, Optional, List
from enum import Enum
import time
import json

logger = logging.getLogger(__name__)

class ProcessingStatus(Enum):
    """Document processing status enumeration"""
    QUEUED = "queued"
    PROCESSING = "processing"
    TEXT_EXTRACTION = "text_extraction"
    TEXT_CHUNKING = "text_chunking"
    EMBEDDING_GENERATION = "embedding_generation"
    VECTOR_STORAGE = "vector_storage"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ProcessingStatusTracker:
    """Tracks processing status for multiple documents"""
    
    def __init__(self):
        self.document_statuses: Dict[str, Dict[str, Any]] = {}
        self.status_history: Dict[str, List[Dict[str, Any]]] = {}
    
    def start_processing(self, document_id: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Start tracking a document's processing status
        
        Args:
            document_id: Document identifier
            metadata: Optional document metadata
            
        Returns:
            True if tracking started successfully
        """
        try:
            self.document_statuses[document_id] = {
                'document_id': document_id,
                'status': ProcessingStatus.QUEUED,
                'started_at': time.time(),
                'updated_at': time.time(),
                'metadata': metadata or {},
                'progress_percentage': 0,
                'current_stage': 'queued',
                'error_message': None,
                'processing_time': 0,
                'stages_completed': []
            }
            
            self.status_history[document_id] = [{
                'status': ProcessingStatus.QUEUED.value,
                'timestamp': time.time(),
                'message': 'Document queued for processing'
            }]
            
            logger.info(f"Started tracking document: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start tracking document {document_id}: {str(e)}")
            return False
    
    def update_status(self, 
                     document_id: str, 
                     status: ProcessingStatus,
                     message: Optional[str] = None,
                     progress_percentage: Optional[int] = None,
                     error_message: Optional[str] = None) -> bool:
        """
        Update document processing status
        
        Args:
            document_id: Document identifier
            status: New processing status
            message: Optional status message
            progress_percentage: Optional progress percentage (0-100)
            error_message: Optional error message
            
        Returns:
            True if update successful
        """
        try:
            if document_id not in self.document_statuses:
                logger.warning(f"Document {document_id} not being tracked, starting tracking")
                self.start_processing(document_id)
            
            doc_status = self.document_statuses[document_id]
            
            # Update status
            old_status = doc_status['status']
            doc_status['status'] = status
            doc_status['updated_at'] = time.time()
            doc_status['current_stage'] = status.value
            
            if progress_percentage is not None:
                doc_status['progress_percentage'] = min(100, max(0, progress_percentage))
            
            if error_message:
                doc_status['error_message'] = error_message
            
            # Calculate processing time
            doc_status['processing_time'] = time.time() - doc_status['started_at']
            
            # Add to stages completed
            if status != old_status and status.value not in doc_status['stages_completed']:
                doc_status['stages_completed'].append(status.value)
            
            # Add to history
            if document_id not in self.status_history:
                self.status_history[document_id] = []
            
            self.status_history[document_id].append({
                'status': status.value,
                'timestamp': time.time(),
                'message': message or f"Status updated to {status.value}",
                'progress_percentage': progress_percentage,
                'error_message': error_message
            })
            
            logger.info(f"Updated status for {document_id}: {old_status.value} → {status.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update status for document {document_id}: {str(e)}")
            return False
    
    def get_document_status(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get current status for a document"""
        return self.document_statuses.get(document_id)
    
    def get_document_history(self, document_id: str) -> List[Dict[str, Any]]:
        """Get status history for a document"""
        return self.status_history.get(document_id, [])
    
    def get_all_statuses(self) -> Dict[str, Dict[str, Any]]:
        """Get current status for all documents"""
        return self.document_statuses.copy()
    
    def get_documents_by_status(self, status: ProcessingStatus) -> List[Dict[str, Any]]:
        """Get all documents with a specific status"""
        return [
            doc_status for doc_status in self.document_statuses.values()
            if doc_status['status'] == status
        ]
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """Get summary of all document processing"""
        if not self.document_statuses:
            return {
                'total_documents': 0,
                'status_breakdown': {},
                'average_processing_time': 0
            }
        
        status_counts = {}
        total_processing_time = 0
        
        for doc_status in self.document_statuses.values():
            status = doc_status['status'].value
            status_counts[status] = status_counts.get(status, 0) + 1
            total_processing_time += doc_status['processing_time']
        
        return {
            'total_documents': len(self.document_statuses),
            'status_breakdown': status_counts,
            'average_processing_time': total_processing_time / len(self.document_statuses),
            'completed_count': status_counts.get(ProcessingStatus.COMPLETED.value, 0),
            'failed_count': status_counts.get(ProcessingStatus.FAILED.value, 0),
            'processing_count': status_counts.get(ProcessingStatus.PROCESSING.value, 0)
        }
    
    def cleanup_old_documents(self, max_age_hours: int = 24):
        """Remove tracking data for old documents"""
        cutoff_time = time.time() - (max_age_hours * 3600)
        documents_to_remove = []
        
        for document_id, doc_status in self.document_statuses.items():
            if doc_status['updated_at'] < cutoff_time:
                documents_to_remove.append(document_id)
        
        for document_id in documents_to_remove:
            del self.document_statuses[document_id]
            if document_id in self.status_history:
                del self.status_history[document_id]
        
        if documents_to_remove:
            logger.info(f"Cleaned up {len(documents_to_remove)} old document tracking records")
        
        return len(documents_to_remove)