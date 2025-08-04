
# File: services/aiml-orchestration/src/reranking/hybrid_reranker.py
"""
Hybrid Reranker - Rerank combined results from multiple sources
Location: services/aiml-orchestration/src/reranking/hybrid_reranker.py
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class HybridReranker:
    """Reranks results from multiple sources considering source diversity"""
    
    def __init__(self):
        self.local_boost = 0.1
        self.web_boost = 0.05
        self.diversity_boost = 0.15
        
    async def rerank_results(
        self, 
        results: List[Dict[str, Any]], 
        query: str
    ) -> List[Dict[str, Any]]:
        """Rerank results considering multiple factors"""
        try:
            if not results:
                return results
            
            # Calculate rerank scores
            for result in results:
                rerank_score = await self._calculate_rerank_score(result, query, results)
                result['rerank_score'] = rerank_score
            
            # Sort by rerank score
            reranked = sorted(results, key=lambda x: x.get('rerank_score', 0.0), reverse=True)
            
            return reranked
            
        except Exception as e:
            logger.error(f"Hybrid reranking error: {e}")
            return results
    
    async def _calculate_rerank_score(
        self, 
        result: Dict[str, Any], 
        query: str, 
        all_results: List[Dict[str, Any]]
    ) -> float:
        """Calculate rerank score for a single result"""
        base_score = result.get('score', 0.0)
        
        # Source type boost
        source_boost = 0.0
        if result.get('result_source') == 'local':
            source_boost = self.local_boost
        elif result.get('result_source') == 'web':
            source_boost = self.web_boost
        
        # Diversity boost (favor results from underrepresented sources)
        diversity_boost = await self._calculate_diversity_boost(result, all_results)
        
        # Query relevance boost
        relevance_boost = await self._calculate_relevance_boost(result, query)
        
        return base_score + source_boost + diversity_boost + relevance_boost
    
    async def _calculate_diversity_boost(
        self, 
        result: Dict[str, Any], 
        all_results: List[Dict[str, Any]]
    ) -> float:
        """Calculate boost for source diversity"""
        result_source = result.get('result_source', 'unknown')
        
        # Count results from same source
        same_source_count = sum(
            1 for r in all_results 
            if r.get('result_source') == result_source
        )
        
        # Boost if this source is underrepresented
        if same_source_count <= 2:
            return self.diversity_boost
        
        return 0.0
    
    async def _calculate_relevance_boost(self, result: Dict[str, Any], query: str) -> float:
        """Calculate boost based on query relevance"""
        content = result.get('content', '').lower()
        title = result.get('title', '').lower()
        query_lower = query.lower()
        
        # Simple keyword matching boost
        query_words = query_lower.split()
        matches = sum(1 for word in query_words if word in content or word in title)
        
        return min(matches * 0.02, 0.1)  # Cap at 0.1
