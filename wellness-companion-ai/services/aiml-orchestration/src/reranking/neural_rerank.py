
# ==== FILE 2: services/aiml-orchestration/src/reranking/neural_rerank.py ====

"""
Neural reranking models for improving search result relevance.
Advanced reranking algorithms using embeddings and ML techniques.
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import sys

sys.path.append('/app/src')

logger = logging.getLogger(__name__)

@dataclass
class RerankResult:
    """Reranking result with new scores and ordering."""
    reranked_results: List[Dict[str, Any]]
    original_results: List[Dict[str, Any]]
    score_improvements: List[float]
    rerank_confidence: float
    processing_time: float
    metadata: Dict[str, Any]

class NeuralRerank:
    """
    Neural reranking system for improving search result quality.
    """
    
    def __init__(self):
        self.rerank_stats = {
            'total_reranks': 0,
            'successful_reranks': 0,
            'failed_reranks': 0,
            'average_rerank_time': 0.0,
            'total_rerank_time': 0.0,
            'average_score_improvement': 0.0,
            'total_score_improvement': 0.0
        }
        
        # Reranking parameters
        self.config = {
            'similarity_weight': 0.4,
            'diversity_weight': 0.2,
            'freshness_weight': 0.1,
            'authority_weight': 0.2,
            'query_match_weight': 0.1,
            'min_score_threshold': 0.1,
            'max_results': 20
        }

    async def rerank_results(
        self,
        results: List[Dict[str, Any]],
        query: str,
        query_embedding: Optional[List[float]] = None,
        rerank_method: str = 'hybrid'
    ) -> RerankResult:
        """
        Rerank search results using neural methods.
        
        Args:
            results: Original search results
            query: Original query text
            query_embedding: Optional query embedding
            rerank_method: Reranking method ('similarity', 'diversity', 'hybrid')
            
        Returns:
            RerankResult with improved ordering
        """
        start_time = datetime.now()
        
        try:
            if not results:
                return self._create_empty_rerank_result(query, start_time)
            
            logger.debug(f"Reranking {len(results)} results using {rerank_method} method")
            
            # Prepare results for reranking
            prepared_results = self._prepare_results(results)
            
            # Apply reranking method
            if rerank_method == 'similarity':
                reranked_results = await self._similarity_rerank(prepared_results, query, query_embedding)
            elif rerank_method == 'diversity':
                reranked_results = await self._diversity_rerank(prepared_results, query)
            elif rerank_method == 'hybrid':
                reranked_results = await self._hybrid_rerank(prepared_results, query, query_embedding)
            else:
                logger.warning(f"Unknown rerank method: {rerank_method}, using hybrid")
                reranked_results = await self._hybrid_rerank(prepared_results, query, query_embedding)
            
            # Calculate improvements
            score_improvements = self._calculate_score_improvements(results, reranked_results)
            rerank_confidence = self._calculate_rerank_confidence(reranked_results, score_improvements)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            rerank_result = RerankResult(
                reranked_results=reranked_results,
                original_results=results,
                score_improvements=score_improvements,
                rerank_confidence=rerank_confidence,
                processing_time=processing_time,
                metadata={
                    'rerank_method': rerank_method,
                    'original_count': len(results),
                    'reranked_count': len(reranked_results),
                    'timestamp': datetime.now().isoformat(),
                    'config_used': self.config.copy()
                }
            )
            
            self._update_stats(True, processing_time, score_improvements)
            logger.info(f"Reranking completed: {len(reranked_results)} results, confidence: {rerank_confidence:.2f}")
            
            return rerank_result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_stats(False, processing_time, [])
            logger.error(f"Error in neural reranking: {str(e)}")
            
            return self._create_error_rerank_result(results, query, str(e), processing_time)

    def _prepare_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare results for reranking by normalizing and enriching."""
        prepared = []
        
        for i, result in enumerate(results):
            prepared_result = result.copy()
            
            # Ensure required fields
            if 'score' not in prepared_result:
                prepared_result['score'] = 0.5
            
            if 'content' not in prepared_result and 'text' in prepared_result:
                prepared_result['content'] = prepared_result['text']
            elif 'content' not in prepared_result:
                prepared_result['content'] = str(prepared_result)
            
            # Add position information
            prepared_result['original_position'] = i
            prepared_result['normalized_score'] = min(1.0, max(0.0, prepared_result['score']))
            
            # Add metadata for reranking
            prepared_result['content_length'] = len(prepared_result['content'])
            prepared_result['word_count'] = len(prepared_result['content'].split())
            
            prepared.append(prepared_result)
        
        return prepared

    async def _similarity_rerank(
        self,
        results: List[Dict[str, Any]],
        query: str,
        query_embedding: Optional[List[float]] = None
    ) -> List[Dict[str, Any]]:
        """Rerank based on semantic similarity."""
        
        # If no query embedding provided, use text-based similarity
        if not query_embedding:
            return self._text_similarity_rerank(results, query)
        
        # Calculate semantic similarities
        for result in results:
            content_embedding = await self._get_content_embedding(result['content'])
            if content_embedding:
                similarity = self._cosine_similarity(query_embedding, content_embedding)
                result['rerank_score'] = (
                    result['normalized_score'] * 0.3 + 
                    similarity * 0.7
                )
            else:
                result['rerank_score'] = result['normalized_score']
        
        # Sort by rerank score
        return sorted(results, key=lambda x: x['rerank_score'], reverse=True)

    def _text_similarity_rerank(self, results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Rerank based on text similarity metrics."""
        query_words = set(query.lower().split())
        
        for result in results:
            content_words = set(result['content'].lower().split())
            
            # Calculate Jaccard similarity
            intersection = len(query_words.intersection(content_words))
            union = len(query_words.union(content_words))
            jaccard_sim = intersection / union if union > 0 else 0
            
            # Calculate word overlap ratio
            overlap_ratio = intersection / len(query_words) if query_words else 0
            
            # Combine similarity metrics
            text_similarity = (jaccard_sim * 0.6 + overlap_ratio * 0.4)
            
            result['rerank_score'] = (
                result['normalized_score'] * 0.4 + 
                text_similarity * 0.6
            )
        
        return sorted(results, key=lambda x: x['rerank_score'], reverse=True)

    async def _diversity_rerank(self, results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Rerank to maximize diversity while maintaining relevance."""
        if len(results) <= 1:
            return results
        
        reranked = []
        remaining = results.copy()
        
        # Start with highest scoring result
        remaining.sort(key=lambda x: x['normalized_score'], reverse=True)
        reranked.append(remaining.pop(0))
        
        # Iteratively add most diverse results
        while remaining and len(reranked) < self.config['max_results']:
            best_candidate = None
            best_diversity_score = -1
            
            for candidate in remaining:
                # Calculate diversity score relative to already selected results
                diversity_score = self._calculate_diversity_score(candidate, reranked)
                combined_score = (
                    candidate['normalized_score'] * 0.6 + 
                    diversity_score * 0.4
                )
                
                if combined_score > best_diversity_score:
                    best_diversity_score = combined_score
                    best_candidate = candidate
            
            if best_candidate:
                best_candidate['rerank_score'] = best_diversity_score
                reranked.append(best_candidate)
                remaining.remove(best_candidate)
        
        return reranked

    async def _hybrid_rerank(
        self,
        results: List[Dict[str, Any]],
        query: str,
        query_embedding: Optional[List[float]] = None
    ) -> List[Dict[str, Any]]:
        """Hybrid reranking combining multiple factors."""
        
        for result in results:
            scores = {}
            
            # 1. Original relevance score
            scores['relevance'] = result['normalized_score']
            
            # 2. Text similarity score
            query_words = set(query.lower().split())
            content_words = set(result['content'].lower().split())
            overlap = len(query_words.intersection(content_words))
            scores['text_similarity'] = overlap / len(query_words) if query_words else 0
            
            # 3. Content quality score (based on length, structure)
            scores['content_quality'] = self._calculate_content_quality(result)
            
            # 4. Freshness score (if timestamp available)
            scores['freshness'] = self._calculate_freshness_score(result)
            
            # 5. Authority score (if source information available)
            scores['authority'] = self._calculate_authority_score(result)
            
            # Combine scores with weights
            result['rerank_score'] = (
                scores['relevance'] * self.config['similarity_weight'] +
                scores['text_similarity'] * self.config['query_match_weight'] +
                scores['content_quality'] * self.config['diversity_weight'] +
                scores['freshness'] * self.config['freshness_weight'] +
                scores['authority'] * self.config['authority_weight']
            )
            
            # Store individual scores for analysis
            result['rerank_scores_breakdown'] = scores
        
        # Sort by final rerank score
        return sorted(results, key=lambda x: x['rerank_score'], reverse=True)

    def _calculate_diversity_score(self, candidate: Dict[str, Any], selected: List[Dict[str, Any]]) -> float:
        """Calculate diversity score relative to already selected results."""
        if not selected:
            return 1.0
        
        candidate_words = set(candidate['content'].lower().split())
        
        similarities = []
        for selected_result in selected:
            selected_words = set(selected_result['content'].lower().split())
            
            # Calculate Jaccard similarity
            intersection = len(candidate_words.intersection(selected_words))
            union = len(candidate_words.union(selected_words))
            similarity = intersection / union if union > 0 else 0
            similarities.append(similarity)
        
        # Diversity is inverse of maximum similarity
        max_similarity = max(similarities) if similarities else 0
        return 1.0 - max_similarity

    def _calculate_content_quality(self, result: Dict[str, Any]) -> float:
        """Calculate content quality score."""
        content = result.get('content', '')
        
        quality_score = 0.5  # Base score
        
        # Length appropriateness
        length = len(content)
        if 100 <= length <= 1000:  # Optimal range
            quality_score += 0.2
        elif 50 <= length < 100 or 1000 < length <= 2000:
            quality_score += 0.1
        
        # Sentence structure
        sentences = content.count('.') + content.count('!') + content.count('?')
        if sentences >= 2:
            quality_score += 0.1
        
        # Word diversity
        words = content.lower().split()
        unique_words = len(set(words))
        if words and unique_words / len(words) > 0.5:  # Good word diversity
            quality_score += 0.1
        
        # Capitalization (proper formatting)
        if content and content[0].isupper():
            quality_score += 0.05
        
        return min(1.0, quality_score)

    def _calculate_freshness_score(self, result: Dict[str, Any]) -> float:
        """Calculate freshness score based on timestamp."""
        # If no timestamp available, assume neutral freshness
        if 'timestamp' not in result and 'date' not in result:
            return 0.5
        
        # For now, return neutral score (can be enhanced with actual date parsing)
        return 0.5

    def _calculate_authority_score(self, result: Dict[str, Any]) -> float:
        """Calculate authority score based on source."""
        source = result.get('source', '').lower()
        
        # Authority based on source type
        if any(domain in source for domain in ['wikipedia', 'edu', 'gov']):
            return 0.9
        elif any(domain in source for domain in ['org', 'com']):
            return 0.7
        else:
            return 0.5

    async def _get_content_embedding(self, content: str) -> Optional[List[float]]:
        """Get embedding for content (placeholder for actual embedding service)."""
        # This would integrate with actual embedding service
        # For now, return None to fall back to text similarity
        return None

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        try:
            vec1_np = np.array(vec1)
            vec2_np = np.array(vec2)
            
            dot_product = np.dot(vec1_np, vec2_np)
            norm1 = np.linalg.norm(vec1_np)
            norm2 = np.linalg.norm(vec2_np)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
        except Exception:
            return 0.0

    def _calculate_score_improvements(
        self,
        original: List[Dict[str, Any]],
        reranked: List[Dict[str, Any]]
    ) -> List[float]:
        """Calculate score improvements from reranking."""
        improvements = []
        
        # Create mapping of results
        original_positions = {
            id(result): i for i, result in enumerate(original)
        }
        
        for new_pos, result in enumerate(reranked):
            original_pos = original_positions.get(id(result), new_pos)
            
            # Position improvement (lower is better for position)
            position_improvement = original_pos - new_pos
            
            # Score improvement
            original_score = result.get('score', 0)
            rerank_score = result.get('rerank_score', original_score)
            score_improvement = rerank_score - original_score
            
            # Combined improvement
            total_improvement = position_improvement * 0.3 + score_improvement * 0.7
            improvements.append(total_improvement)
        
        return improvements

    def _calculate_rerank_confidence(
        self,
        reranked_results: List[Dict[str, Any]],
        score_improvements: List[float]
    ) -> float:
        """Calculate confidence in reranking quality."""
        if not reranked_results or not score_improvements:
            return 0.5
        
        confidence = 0.5  # Base confidence
        
        # Improvement factor
        avg_improvement = sum(score_improvements) / len(score_improvements)
        if avg_improvement > 0:
            confidence += min(0.3, avg_improvement * 0.5)
        
        # Score distribution factor
        scores = [r.get('rerank_score', 0) for r in reranked_results]
        if scores:
            score_variance = np.var(scores)
            if score_variance > 0.1:  # Good score separation
                confidence += 0.1
        
        # Top result quality factor
        if reranked_results and reranked_results[0].get('rerank_score', 0) > 0.8:
            confidence += 0.1
        
        return min(1.0, confidence)

    def _create_empty_rerank_result(self, query: str, start_time: datetime) -> RerankResult:
        """Create empty rerank result."""
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return RerankResult(
            reranked_results=[],
            original_results=[],
            score_improvements=[],
            rerank_confidence=0.0,
            processing_time=processing_time,
            metadata={
                'query': query,
                'reason': 'No results to rerank',
                'timestamp': datetime.now().isoformat()
            }
        )

    def _create_error_rerank_result(
        self,
        original_results: List[Dict[str, Any]],
        query: str,
        error: str,
        processing_time: float
    ) -> RerankResult:
        """Create error rerank result."""
        return RerankResult(
            reranked_results=original_results,  # Return original on error
            original_results=original_results,
            score_improvements=[0.0] * len(original_results),
            rerank_confidence=0.0,
            processing_time=processing_time,
            metadata={
                'query': query,
                'error': error,
                'timestamp': datetime.now().isoformat()
            }
        )

    def _update_stats(self, success: bool, processing_time: float, score_improvements: List[float]):
        """Update reranking statistics."""
        self.rerank_stats['total_reranks'] += 1
        
        if success:
            self.rerank_stats['successful_reranks'] += 1
            
            if score_improvements:
                avg_improvement = sum(score_improvements) / len(score_improvements)
                self.rerank_stats['total_score_improvement'] += avg_improvement
                self.rerank_stats['average_score_improvement'] = (
                    self.rerank_stats['total_score_improvement'] / 
                    self.rerank_stats['successful_reranks']
                )
        else:
            self.rerank_stats['failed_reranks'] += 1
        
        self.rerank_stats['total_rerank_time'] += processing_time
        self.rerank_stats['average_rerank_time'] = (
            self.rerank_stats['total_rerank_time'] / 
            self.rerank_stats['total_reranks']
        )

    def get_reranking_statistics(self) -> Dict[str, Any]:
        """Get reranking performance statistics."""
        return {
            **self.rerank_stats,
            'success_rate': f"{(self.rerank_stats['successful_reranks'] / max(1, self.rerank_stats['total_reranks'])) * 100:.2f}%"
        }

    def update_config(self, config_updates: Dict[str, Any]):
        """Update reranking configuration."""
        self.config.update(config_updates)
        logger.info(f"Reranking config updated: {config_updates}")
