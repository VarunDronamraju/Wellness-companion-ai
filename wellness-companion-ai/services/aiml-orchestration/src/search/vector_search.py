
# File 1: services/aiml-orchestration/src/search/vector_search.py
"""
Cosine similarity search implementation with configurable thresholds.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
import time
from .qdrant_client import QdrantClientManager
from .similarity_calculator import SimilarityCalculator

logger = logging.getLogger(__name__)

class VectorSearch:
    """High-level vector search interface with similarity calculations"""
    
    def __init__(self, default_threshold: float = 0.7):
        self.qdrant_client = QdrantClientManager()
        self.similarity_calculator = SimilarityCalculator()
        self.default_threshold = default_threshold
        self.search_stats = {
            'total_searches': 0,
            'successful_searches': 0,
            'failed_searches': 0,
            'total_results_returned': 0,
            'average_search_time': 0.0,
            'total_search_time': 0.0
        }
        
        # Ensure connection
        if not self.qdrant_client.connected:
            self.qdrant_client.connect()
    
    def search_similar_documents(self,
                               query_vector: List[float],
                               collection_name: str = "documents",
                               limit: int = 10,
                               score_threshold: Optional[float] = None,
                               filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Search for similar documents using vector similarity
        
        Args:
            query_vector: Query embedding vector
            collection_name: Collection to search in
            limit: Maximum number of results
            score_threshold: Minimum similarity score (uses default if None)
            filters: Optional metadata filters
            
        Returns:
            Search results with similarity scores
        """
        start_time = time.time()
        self.search_stats['total_searches'] += 1
        
        try:
            # Use default threshold if not provided
            threshold = score_threshold if score_threshold is not None else self.default_threshold
            
            # Validate query vector
            if not query_vector or not isinstance(query_vector, list):
                return {
                    'success': False,
                    'error': 'Invalid query vector',
                    'results': []
                }
            
            # Perform vector search
            search_results = self.qdrant_client.search_vectors(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=threshold
            )
            
            # Process and enhance results
            enhanced_results = []
            for result in search_results:
                enhanced_result = {
                    'id': result['id'],
                    'score': result['score'],
                    'similarity_percentage': f"{result['score'] * 100:.2f}%",
                    'payload': result['payload'],
                    'document_id': result['payload'].get('document_id'),
                    'text': result['payload'].get('text', ''),
                    'chunk_index': result['payload'].get('chunk_index', 0),
                    'relevance_category': self._categorize_relevance(result['score'])
                }
                enhanced_results.append(enhanced_result)
            
            search_time = time.time() - start_time
            
            # Update statistics
            self.search_stats['successful_searches'] += 1
            self.search_stats['total_results_returned'] += len(enhanced_results)
            self.search_stats['total_search_time'] += search_time
            self.search_stats['average_search_time'] = (
                self.search_stats['total_search_time'] / 
                self.search_stats['successful_searches']
            )
            
            logger.info(f"Vector search completed: {len(enhanced_results)} results in {search_time:.3f}s")
            
            return {
                'success': True,
                'results': enhanced_results,
                'search_metadata': {
                    'query_vector_dimension': len(query_vector),
                    'collection': collection_name,
                    'limit': limit,
                    'score_threshold': threshold,
                    'results_count': len(enhanced_results),
                    'search_time': search_time,
                    'filters_applied': filters is not None
                }
            }
            
        except Exception as e:
            self.search_stats['failed_searches'] += 1
            logger.error(f"Vector search failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'results': [],
                'search_time': time.time() - start_time
            }
    
    def _categorize_relevance(self, score: float) -> str:
        """Categorize relevance based on similarity score"""
        if score >= 0.9:
            return "highly_relevant"
        elif score >= 0.8:
            return "very_relevant"
        elif score >= 0.7:
            return "relevant"
        elif score >= 0.6:
            return "somewhat_relevant"
        else:
            return "low_relevance"
    
    def search_with_reranking(self,
                            query_vector: List[float],
                            query_text: str,
                            collection_name: str = "documents",
                            limit: int = 20,
                            final_limit: int = 10,
                            score_threshold: Optional[float] = None) -> Dict[str, Any]:
        """
        Search with text-based reranking for improved relevance
        
        Args:
            query_vector: Query embedding vector
            query_text: Original query text for reranking
            collection_name: Collection to search
            limit: Initial search limit (higher for reranking)
            final_limit: Final number of results after reranking
            score_threshold: Minimum similarity score
            
        Returns:
            Reranked search results
        """
        try:
            # Get initial results with higher limit
            initial_results = self.search_similar_documents(
                query_vector=query_vector,
                collection_name=collection_name,
                limit=limit,
                score_threshold=score_threshold
            )
            
            if not initial_results['success'] or not initial_results['results']:
                return initial_results
            
            # Perform text-based reranking
            reranked_results = self.similarity_calculator.rerank_by_text_similarity(
                query_text=query_text,
                search_results=initial_results['results'],
                final_limit=final_limit
            )
            
            return {
                'success': True,
                'results': reranked_results,
                'search_metadata': {
                    **initial_results['search_metadata'],
                    'reranking_applied': True,
                    'initial_results_count': len(initial_results['results']),
                    'final_results_count': len(reranked_results)
                }
            }
            
        except Exception as e:
            logger.error(f"Reranked search failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'results': []
            }
    
    def multi_collection_search(self,
                              query_vector: List[float],
                              collections: List[str],
                              limit_per_collection: int = 5,
                              score_threshold: Optional[float] = None) -> Dict[str, Any]:
        """
        Search across multiple collections and combine results
        
        Args:
            query_vector: Query embedding vector
            collections: List of collection names to search
            limit_per_collection: Limit per collection
            score_threshold: Minimum similarity score
            
        Returns:
            Combined search results from all collections
        """
        try:
            all_results = []
            collection_stats = {}
            
            for collection in collections:
                collection_result = self.search_similar_documents(
                    query_vector=query_vector,
                    collection_name=collection,
                    limit=limit_per_collection,
                    score_threshold=score_threshold
                )
                
                if collection_result['success']:
                    # Add collection info to each result
                    for result in collection_result['results']:
                        result['source_collection'] = collection
                    
                    all_results.extend(collection_result['results'])
                    collection_stats[collection] = {
                        'results_count': len(collection_result['results']),
                        'search_time': collection_result['search_metadata']['search_time']
                    }
                else:
                    collection_stats[collection] = {
                        'results_count': 0,
                        'error': collection_result.get('error', 'Unknown error')
                    }
            
            # Sort all results by score (highest first)
            all_results.sort(key=lambda x: x['score'], reverse=True)
            
            return {
                'success': True,
                'results': all_results,
                'multi_collection_metadata': {
                    'collections_searched': collections,
                    'total_results': len(all_results),
                    'collection_stats': collection_stats
                }
            }
            
        except Exception as e:
            logger.error(f"Multi-collection search failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'results': []
            }
    
    def get_search_statistics(self) -> Dict[str, Any]:
        """Get search performance statistics"""
        total_searches = self.search_stats['total_searches']
        success_rate = (
            (self.search_stats['successful_searches'] / max(total_searches, 1)) * 100
        )
        
        return {
            **self.search_stats,
            'success_rate': f"{success_rate:.2f}%",
            'average_results_per_search': (
                self.search_stats['total_results_returned'] / max(total_searches, 1)
            ),
            'default_threshold': self.default_threshold
        }
    
    def update_default_threshold(self, new_threshold: float) -> bool:
        """Update the default similarity threshold"""
        if 0.0 <= new_threshold <= 1.0:
            old_threshold = self.default_threshold
            self.default_threshold = new_threshold
            logger.info(f"Updated default threshold: {old_threshold} → {new_threshold}")
            return True
        else:
            logger.error(f"Invalid threshold value: {new_threshold}. Must be between 0.0 and 1.0")
            return False
