
# File 2: services/aiml-orchestration/src/search/similarity_calculator.py
"""
Similarity calculation algorithms and utilities.
"""

import logging
from typing import List, Dict, Any, Tuple
import math
import re
from collections import Counter

logger = logging.getLogger(__name__)

class SimilarityCalculator:
    """Implements various similarity calculation methods"""
    
    def __init__(self):
        self.calculation_stats = {
            'cosine_calculations': 0,
            'text_similarity_calculations': 0,
            'total_comparisons': 0
        }
    
    def cosine_similarity(self, vector_a: List[float], vector_b: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors
        
        Args:
            vector_a: First vector
            vector_b: Second vector
            
        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        try:
            self.calculation_stats['cosine_calculations'] += 1
            
            if len(vector_a) != len(vector_b):
                raise ValueError(f"Vector dimensions don't match: {len(vector_a)} vs {len(vector_b)}")
            
            # Calculate dot product
            dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
            
            # Calculate magnitudes
            magnitude_a = math.sqrt(sum(a * a for a in vector_a))
            magnitude_b = math.sqrt(sum(b * b for b in vector_b))
            
            # Avoid division by zero
            if magnitude_a == 0.0 or magnitude_b == 0.0:
                return 0.0
            
            # Calculate cosine similarity
            similarity = dot_product / (magnitude_a * magnitude_b)
            
            # Clamp to [0, 1] range (for normalized vectors, this should be automatic)
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            logger.error(f"Cosine similarity calculation failed: {str(e)}")
            return 0.0
    
    def euclidean_distance(self, vector_a: List[float], vector_b: List[float]) -> float:
        """
        Calculate Euclidean distance between two vectors
        
        Args:
            vector_a: First vector
            vector_b: Second vector
            
        Returns:
            Euclidean distance
        """
        try:
            if len(vector_a) != len(vector_b):
                raise ValueError(f"Vector dimensions don't match: {len(vector_a)} vs {len(vector_b)}")
            
            distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(vector_a, vector_b)))
            return distance
            
        except Exception as e:
            logger.error(f"Euclidean distance calculation failed: {str(e)}")
            return float('inf')
    
    def manhattan_distance(self, vector_a: List[float], vector_b: List[float]) -> float:
        """
        Calculate Manhattan distance between two vectors
        
        Args:
            vector_a: First vector
            vector_b: Second vector
            
        Returns:
            Manhattan distance
        """
        try:
            if len(vector_a) != len(vector_b):
                raise ValueError(f"Vector dimensions don't match: {len(vector_a)} vs {len(vector_b)}")
            
            distance = sum(abs(a - b) for a, b in zip(vector_a, vector_b))
            return distance
            
        except Exception as e:
            logger.error(f"Manhattan distance calculation failed: {str(e)}")
            return float('inf')
    
    def text_similarity(self, text_a: str, text_b: str) -> float:
        """
        Calculate text similarity using word overlap and TF-IDF-like scoring
        
        Args:
            text_a: First text
            text_b: Second text
            
        Returns:
            Text similarity score (0.0 to 1.0)
        """
        try:
            self.calculation_stats['text_similarity_calculations'] += 1
            
            # Preprocess texts
            words_a = self._preprocess_text(text_a)
            words_b = self._preprocess_text(text_b)
            
            if not words_a or not words_b:
                return 0.0
            
            # Calculate word frequency vectors
            counter_a = Counter(words_a)
            counter_b = Counter(words_b)
            
            # Get all unique words
            all_words = set(words_a + words_b)
            
            # Create frequency vectors
            vector_a = [counter_a.get(word, 0) for word in all_words]
            vector_b = [counter_b.get(word, 0) for word in all_words]
            
            # Calculate cosine similarity of frequency vectors
            return self.cosine_similarity(
                [float(x) for x in vector_a],
                [float(x) for x in vector_b]
            )
            
        except Exception as e:
            logger.error(f"Text similarity calculation failed: {str(e)}")
            return 0.0
    
    def _preprocess_text(self, text: str) -> List[str]:
        """Preprocess text for similarity calculation"""
        # Convert to lowercase and extract words
        text = text.lower()
        words = re.findall(r'\b\w+\b', text)
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'
        }
        
        return [word for word in words if word not in stop_words and len(word) > 2]
    
    def rerank_by_text_similarity(self,
                                query_text: str,
                                search_results: List[Dict[str, Any]],
                                final_limit: int = 10) -> List[Dict[str, Any]]:
        """
        Rerank search results by combining vector similarity with text similarity
        
        Args:
            query_text: Original query text
            search_results: Initial search results
            final_limit: Final number of results to return
            
        Returns:
            Reranked results
        """
        try:
            if not search_results:
                return []
            
            # Calculate text similarity for each result
            for result in search_results:
                result_text = result.get('text', '')
                text_sim = self.text_similarity(query_text, result_text)
                
                # Combine vector similarity (score) with text similarity
                vector_sim = result.get('score', 0.0)
                
                # Weighted combination (70% vector similarity, 30% text similarity)
                combined_score = (0.7 * vector_sim) + (0.3 * text_sim)
                
                result['text_similarity'] = text_sim
                result['combined_score'] = combined_score
                result['reranked'] = True
            
            # Sort by combined score
            reranked_results = sorted(
                search_results,
                key=lambda x: x.get('combined_score', 0.0),
                reverse=True
            )
            
            # Return top results
            return reranked_results[:final_limit]
            
        except Exception as e:
            logger.error(f"Reranking failed: {str(e)}")
            return search_results[:final_limit]  # Fallback to original ranking
    
    def batch_similarity_calculation(self,
                                   query_vector: List[float],
                                   candidate_vectors: List[List[float]],
                                   similarity_method: str = "cosine") -> List[float]:
        """
        Calculate similarity scores for multiple candidate vectors
        
        Args:
            query_vector: Query vector
            candidate_vectors: List of candidate vectors
            similarity_method: Similarity method ("cosine", "euclidean", "manhattan")
            
        Returns:
            List of similarity scores
        """
        try:
            self.calculation_stats['total_comparisons'] += len(candidate_vectors)
            
            if similarity_method == "cosine":
                return [
                    self.cosine_similarity(query_vector, candidate)
                    for candidate in candidate_vectors
                ]
            elif similarity_method == "euclidean":
                # Convert distance to similarity (inverse relationship)
                distances = [
                    self.euclidean_distance(query_vector, candidate)
                    for candidate in candidate_vectors
                ]
                max_distance = max(distances) if distances else 1.0
                return [1.0 - (dist / max_distance) for dist in distances]
            elif similarity_method == "manhattan":
                # Convert distance to similarity (inverse relationship)
                distances = [
                    self.manhattan_distance(query_vector, candidate)
                    for candidate in candidate_vectors
                ]
                max_distance = max(distances) if distances else 1.0
                return [1.0 - (dist / max_distance) for dist in distances]
            else:
                raise ValueError(f"Unknown similarity method: {similarity_method}")
                
        except Exception as e:
            logger.error(f"Batch similarity calculation failed: {str(e)}")
            return [0.0] * len(candidate_vectors)
    
    def get_calculation_stats(self) -> Dict[str, Any]:
        """Get similarity calculation statistics"""
        return {
            'cosine_calculations': self.calculation_stats['cosine_calculations'],
            'text_similarity_calculations': self.calculation_stats['text_similarity_calculations'],
            'total_vector_comparisons': self.calculation_stats['total_comparisons'],
            'supported_methods': ['cosine', 'euclidean', 'manhattan', 'text_similarity']
        }
