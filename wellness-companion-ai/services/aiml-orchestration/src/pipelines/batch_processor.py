# services/aiml-orchestration/src/embeddings/batch_processor.py
"""
Batch processing for efficient embedding generation - FIXED VERSION.
"""

import logging
from typing import List, Dict, Iterator, Any
import asyncio
import time  # ADDED MISSING IMPORT
from concurrent.futures import ThreadPoolExecutor, as_completed
from .embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

class BatchEmbeddingProcessor:
    """Efficient batch processing for embeddings"""
    
    def __init__(self, batch_size: int = 32, max_workers: int = 4):
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.embedding_service = EmbeddingService()
        
    def create_batches(self, texts: List[str]) -> Iterator[List[str]]:
        """Split texts into batches"""
        for i in range(0, len(texts), self.batch_size):
            yield texts[i:i + self.batch_size]
    
    def process_batch_sync(self, texts: List[str]) -> Dict[str, Any]:
        """
        Process a batch of texts synchronously
        
        Args:
            texts: List of texts to process
            
        Returns:
            Dict with embeddings and metadata
        """
        try:
            start_time = time.time()
            embeddings = self.embedding_service.generate_embeddings(texts)
            processing_time = time.time() - start_time
            
            return {
                'embeddings': embeddings,
                'texts_count': len(texts),
                'processing_time': processing_time,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Batch processing failed: {str(e)}")
            return {
                'embeddings': [],
                'texts_count': len(texts),
                'processing_time': 0.0,
                'success': False,
                'error': str(e)
            }
    
    def process_large_dataset(self, texts: List[str], show_progress: bool = True) -> Dict[str, Any]:
        """
        Process large dataset with parallel batch processing
        
        Args:
            texts: Large list of texts to process
            show_progress: Whether to show progress information
            
        Returns:
            Combined results with all embeddings
        """
        batches = list(self.create_batches(texts))
        total_batches = len(batches)
        
        logger.info(f"Processing {len(texts)} texts in {total_batches} batches")
        
        all_embeddings = []
        total_processing_time = 0.0
        failed_batches = 0
        
        # Process batches with thread pool
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all batch jobs
            future_to_batch = {
                executor.submit(self.process_batch_sync, batch): i 
                for i, batch in enumerate(batches)
            }
            
            # Collect results as they complete
            batch_results = [None] * total_batches
            
            for future in as_completed(future_to_batch):
                batch_index = future_to_batch[future]
                try:
                    result = future.result()
                    batch_results[batch_index] = result
                    
                    if result['success']:
                        total_processing_time += result['processing_time']
                        if show_progress:
                            completed = sum(1 for r in batch_results if r is not None)
                            progress = (completed / total_batches) * 100
                            logger.info(f"Batch {batch_index + 1}/{total_batches} complete ({progress:.1f}%)")
                    else:
                        failed_batches += 1
                        logger.error(f"Batch {batch_index + 1} failed: {result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    failed_batches += 1
                    logger.error(f"Batch {batch_index + 1} exception: {str(e)}")
                    batch_results[batch_index] = {
                        'embeddings': [],
                        'success': False,
                        'error': str(e)
                    }
        
        # Combine all successful results
        for result in batch_results:
            if result and result['success']:
                all_embeddings.extend(result['embeddings'])
        
        success_rate = ((total_batches - failed_batches) / total_batches) * 100
        
        return {
            'embeddings': all_embeddings,
            'total_texts': len(texts),
            'successful_embeddings': len(all_embeddings),
            'total_batches': total_batches,
            'failed_batches': failed_batches,
            'success_rate': f"{success_rate:.2f}%",
            'total_processing_time': total_processing_time,
            'average_time_per_text': total_processing_time / len(texts) if texts else 0
        }
    
    def get_optimal_batch_size(self, sample_texts: List[str]) -> int:
        """
        Determine optimal batch size based on performance testing
        
        Args:
            sample_texts: Sample texts for testing different batch sizes
            
        Returns:
            Optimal batch size
        """
        if len(sample_texts) < 10:
            return min(len(sample_texts), 32)
        
        test_sizes = [8, 16, 32, 64]
        performance_results = {}
        
        # Test each batch size
        for batch_size in test_sizes:
            if batch_size > len(sample_texts):
                continue
                
            test_batch = sample_texts[:batch_size]
            
            start_time = time.time()
            result = self.process_batch_sync(test_batch)
            end_time = time.time()
            
            if result['success']:
                time_per_text = (end_time - start_time) / batch_size
                performance_results[batch_size] = time_per_text
        
        if not performance_results:
            return 32  # Default fallback
        
        # Return batch size with best time per text
        optimal_size = min(performance_results.keys(), key=lambda x: performance_results[x])
        logger.info(f"Optimal batch size determined: {optimal_size}")
        
        return optimal_size