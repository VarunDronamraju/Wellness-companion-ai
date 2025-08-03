# services/aiml-orchestration/src/embeddings/embedding_service.py
"""
Main embedding generation service with batch processing and caching.
"""

import logging
from typing import List, Dict, Optional, Any
from .model_manager import EmbeddingModelManager
from .embedding_config import EmbeddingConfig
import hashlib
import json
import time  # ADDED MISSING IMPORT

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Main service for generating embeddings with optimization"""
    
    def __init__(self, config: EmbeddingConfig = None):
        self.config = config or EmbeddingConfig()
        self.model_manager = EmbeddingModelManager()
        self.cache = {}  # Simple in-memory cache
        self.stats = {
            'total_requests': 0,
            'cache_hits': 0,
            'total_texts_processed': 0,
            'total_processing_time': 0.0
        }
        
        # Initialize default model
        model_name = self.config.get('model', 'name')
        self.model_manager.load_model(model_name)
    
    def generate_single_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text to embed
            
        Returns:
            Embedding vector
        """
        return self.generate_embeddings([text])[0]
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts with caching
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        start_time = time.time()
        self.stats['total_requests'] += 1
        self.stats['total_texts_processed'] += len(texts)
        
        try:
            # Check cache for existing embeddings
            cached_embeddings = {}
            uncached_texts = []
            uncached_indices = []
            
            for i, text in enumerate(texts):
                text_hash = self._get_text_hash(text)
                if text_hash in self.cache:
                    cached_embeddings[i] = self.cache[text_hash]
                    self.stats['cache_hits'] += 1
                else:
                    uncached_texts.append(text)
                    uncached_indices.append(i)
            
            # Generate embeddings for uncached texts
            new_embeddings = []
            if uncached_texts:
                logger.info(f"Generating embeddings for {len(uncached_texts)} texts")
                new_embeddings = self.model_manager.generate_embeddings(uncached_texts)
                
                # Cache new embeddings
                for text, embedding in zip(uncached_texts, new_embeddings):
                    text_hash = self._get_text_hash(text)
                    self.cache[text_hash] = embedding
            
            # Combine cached and new embeddings in correct order
            result_embeddings = [None] * len(texts)
            
            # Fill cached embeddings
            for index, embedding in cached_embeddings.items():
                result_embeddings[index] = embedding
            
            # Fill new embeddings
            for i, embedding in enumerate(new_embeddings):
                original_index = uncached_indices[i]
                result_embeddings[original_index] = embedding
            
            processing_time = time.time() - start_time
            self.stats['total_processing_time'] += processing_time
            
            logger.info(f"Generated {len(result_embeddings)} embeddings in {processing_time:.3f}s")
            return result_embeddings
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            raise
    
    def _get_text_hash(self, text: str) -> str:
        """Generate hash for text caching"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def clear_cache(self):
        """Clear the embedding cache"""
        self.cache.clear()
        logger.info("Embedding cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        cache_hit_rate = (self.stats['cache_hits'] / max(self.stats['total_texts_processed'], 1)) * 100
        avg_processing_time = self.stats['total_processing_time'] / max(self.stats['total_requests'], 1)
        
        return {
            **self.stats,
            'cache_hit_rate': f"{cache_hit_rate:.2f}%",
            'average_processing_time': f"{avg_processing_time:.3f}s",
            'cache_size': len(self.cache),
            'model_info': self.model_manager.get_status()
        }
    
    def validate_embeddings(self, embeddings: List[List[float]]) -> Dict[str, Any]:
        """Validate embedding quality and consistency"""
        if not embeddings:
            return {'valid': False, 'error': 'No embeddings provided'}
        
        try:
            # Check dimensions consistency
            expected_dim = self.model_manager.SUPPORTED_MODELS[self.model_manager.current_model_name]['dimensions']
            
            dimension_check = all(len(emb) == expected_dim for emb in embeddings)
            
            # Check for NaN or infinite values
            import math
            quality_check = all(
                all(math.isfinite(val) for val in emb) 
                for emb in embeddings
            )
            
            return {
                'valid': dimension_check and quality_check,
                'dimension_check': dimension_check,
                'quality_check': quality_check,
                'expected_dimension': expected_dim,
                'actual_dimensions': [len(emb) for emb in embeddings[:5]]  # First 5 for debugging
            }
            
        except Exception as e:
            return {'valid': False, 'error': str(e)}