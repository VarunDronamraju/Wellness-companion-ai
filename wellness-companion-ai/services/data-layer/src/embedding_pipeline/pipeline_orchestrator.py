
# File 2: services/data-layer/src/embedding_pipeline/pipeline_orchestrator.py
"""
Pipeline coordination and management for multiple documents.
"""

import logging
from typing import List, Dict, Any, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from .ingestion_pipeline import DocumentIngestionPipeline

logger = logging.getLogger(__name__)

class PipelineOrchestrator:
    """Orchestrates multiple document processing pipelines"""
    
    def __init__(self, max_concurrent_documents: int = 3):
        self.max_concurrent_documents = max_concurrent_documents
        self.pipelines = {}  # document_id -> pipeline instance
        self.processing_queue = []
        self.completed_documents = []
        self.failed_documents = []
        
    def add_document_to_queue(self, 
                            file_path: str,
                            document_id: str,
                            metadata: Optional[Dict[str, Any]] = None,
                            priority: int = 0) -> bool:
        """
        Add a document to the processing queue
        
        Args:
            file_path: Path to document file
            document_id: Unique document identifier
            metadata: Optional document metadata
            priority: Processing priority (higher = sooner)
            
        Returns:
            True if added successfully
        """
        try:
            document_info = {
                'file_path': file_path,
                'document_id': document_id,
                'metadata': metadata or {},
                'priority': priority,
                'queued_at': time.time()
            }
            
            self.processing_queue.append(document_info)
            # Sort by priority (higher first)
            self.processing_queue.sort(key=lambda x: x['priority'], reverse=True)
            
            logger.info(f"Added document {document_id} to processing queue (priority: {priority})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add document {document_id} to queue: {str(e)}")
            return False
    
    def process_queue_batch(self) -> Dict[str, Any]:
        """
        Process all documents in the queue using concurrent processing
        
        Returns:
            Batch processing results
        """
        if not self.processing_queue:
            return {
                'success': True,
                'message': 'No documents in queue',
                'processed_count': 0,
                'failed_count': 0
            }
        
        start_time = time.time()
        documents_to_process = self.processing_queue.copy()
        self.processing_queue.clear()
        
        logger.info(f"Processing batch of {len(documents_to_process)} documents")
        
        successful_results = []
        failed_results = []
        
        # Process documents with thread pool
        with ThreadPoolExecutor(max_workers=self.max_concurrent_documents) as executor:
            # Submit all document processing jobs
            future_to_doc = {}
            
            for doc_info in documents_to_process:
                pipeline = DocumentIngestionPipeline()
                future = executor.submit(
                    pipeline.process_document,
                    doc_info['file_path'],
                    doc_info['document_id'],
                    doc_info['metadata']
                )
                future_to_doc[future] = doc_info
            
            # Collect results as they complete
            for future in as_completed(future_to_doc):
                doc_info = future_to_doc[future]
                document_id = doc_info['document_id']
                
                try:
                    result = future.result()
                    result['queue_info'] = doc_info
                    
                    if result['success']:
                        successful_results.append(result)
                        self.completed_documents.append(result)
                        logger.info(f"Successfully processed document: {document_id}")
                    else:
                        failed_results.append(result)
                        self.failed_documents.append(result)
                        logger.error(f"Failed to process document {document_id}: {result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    error_result = {
                        'success': False,
                        'document_id': document_id,
                        'error': str(e),
                        'stage': 'executor_exception',
                        'queue_info': doc_info
                    }
                    failed_results.append(error_result)
                    self.failed_documents.append(error_result)
                    logger.error(f"Executor exception for document {document_id}: {str(e)}")
        
        processing_time = time.time() - start_time
        success_rate = (len(successful_results) / len(documents_to_process)) * 100
        
        return {
            'success': len(failed_results) == 0,
            'processing_time': processing_time,
            'total_documents': len(documents_to_process),
            'successful_count': len(successful_results),
            'failed_count': len(failed_results),
            'success_rate': f"{success_rate:.2f}%",
            'successful_results': successful_results,
            'failed_results': failed_results,
            'average_time_per_document': processing_time / len(documents_to_process)
        }
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue and processing status"""
        return {
            'queue_size': len(self.processing_queue),
            'completed_documents': len(self.completed_documents),
            'failed_documents': len(self.failed_documents),
            'max_concurrent': self.max_concurrent_documents,
            'queued_documents': [
                {
                    'document_id': doc['document_id'],
                    'priority': doc['priority'],
                    'queued_at': doc['queued_at']
                }
                for doc in self.processing_queue
            ]
        }
    
    def clear_history(self):
        """Clear completed and failed document history"""
        self.completed_documents.clear()
        self.failed_documents.clear()
        logger.info("Cleared processing history")
