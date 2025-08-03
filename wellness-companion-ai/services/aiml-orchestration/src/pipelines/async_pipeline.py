
# File 5: services/aiml-orchestration/src/pipelines/async_pipeline.py
"""
Asynchronous pipeline for high-throughput embedding processing.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
import time
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class AsyncEmbeddingPipeline:
    """Asynchronous pipeline for embedding processing"""
    
    def __init__(self, max_concurrent_documents: int = 3):
        self.max_concurrent_documents = max_concurrent_documents
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_documents)
        self.active_tasks = {}
        
    async def process_document_async(self, 
                                   document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single document asynchronously
        
        Args:
            document_data: Document with chunks and metadata
            
        Returns:
            Processing result
        """
        document_id = document_data.get('document_id', 'unknown')
        
        try:
            # Import here to avoid circular imports
            from .batch_processor import EmbeddingPipeline
            
            pipeline = EmbeddingPipeline()
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor,
                pipeline.process_document_chunks,
                document_data.get('chunks', []),
                document_id
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Async processing failed for document {document_id}: {str(e)}")
            return {
                'success': False,
                'document_id': document_id,
                'error': str(e)
            }
    
    async def process_multiple_documents(self, 
                                       documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process multiple documents concurrently
        
        Args:
            documents: List of document data
            
        Returns:
            List of processing results
        """
        if not documents:
            return []
        
        logger.info(f"Processing {len(documents)} documents asynchronously")
        
        # Create tasks for all documents
        tasks = [
            asyncio.create_task(self.process_document_async(doc))
            for doc in documents
        ]
        
        # Track active tasks
        for i, task in enumerate(tasks):
            doc_id = documents[i].get('document_id', f'doc_{i}')
            self.active_tasks[doc_id] = task
        
        try:
            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results and handle exceptions
            processed_results = []
            for i, result in enumerate(results):
                doc_id = documents[i].get('document_id', f'doc_{i}')
                
                if isinstance(result, Exception):
                    processed_results.append({
                        'success': False,
                        'document_id': doc_id,
                        'error': str(result)
                    })
                else:
                    processed_results.append(result)
                
                # Remove from active tasks
                self.active_tasks.pop(doc_id, None)
            
            return processed_results
            
        except Exception as e:
            logger.error(f"Batch async processing failed: {str(e)}")
            return [
                {
                    'success': False,
                    'document_id': doc.get('document_id', f'doc_{i}'),
                    'error': str(e)
                }
                for i, doc in enumerate(documents)
            ]
    
    def get_active_tasks(self) -> Dict[str, str]:
        """Get status of active processing tasks"""
        return {
            doc_id: 'running' if not task.done() else 'completed'
            for doc_id, task in self.active_tasks.items()
        }
    
    async def cancel_document_processing(self, document_id: str) -> bool:
        """Cancel processing for a specific document"""
        if document_id in self.active_tasks:
            task = self.active_tasks[document_id]
            if not task.done():
                task.cancel()
                logger.info(f"Cancelled processing for document: {document_id}")
                return True
        return False
    
    def cleanup(self):
        """Cleanup resources"""
        # Cancel all active tasks
        for task in self.active_tasks.values():
            if not task.done():
                task.cancel()
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("Async pipeline cleaned up")