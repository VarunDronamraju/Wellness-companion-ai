
# File: services/aiml-orchestration/src/orchestrators/search_coordinator.py
"""
Search Coordinator - Coordinate between vector and web search
Location: services/aiml-orchestration/src/orchestrators/search_coordinator.py
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class SearchCoordinator:
    """Coordinates results from vector search and web search"""
    
    def __init__(self):
        self.max_combined_results = 20
        
    async def coordinate_results(
        self, 
        vector_results: List[Dict[str, Any]], 
        web_results: List[Dict[str, Any]], 
        query: str
    ) -> List[Dict[str, Any]]:
        """Coordinate and merge results from different search sources"""
        try:
            combined_results = []
            
            # Add vector results with source annotation
            for result in vector_results:
                result_copy = result.copy()
                result_copy['source'] = 'vector_search'
                result_copy['search_type'] = 'local'
                combined_results.append(result_copy)
            
            # Add web results with source annotation
            for result in web_results:
                result_copy = result.copy()
                result_copy['source'] = 'web_search'
                result_copy['search_type'] = 'web'
                combined_results.append(result_copy)
            
            # Remove duplicates based on content similarity
            deduplicated = await self._remove_duplicates(combined_results)
            
            # Rerank combined results
            reranked = await self._rerank_results(deduplicated, query)
            
            # Limit results
            final_results = reranked[:self.max_combined_results]
            
            logger.info(f"Coordinated {len(final_results)} results from {len(vector_results)} vector + {len(web_results)} web")
            return final_results
            
        except Exception as e:
            logger.error(f"Result coordination error: {e}")
            return vector_results + web_results  # Fallback to simple concatenation
    
    async def _remove_duplicates(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate results based on content similarity"""
        if len(results) <= 1:
            return results
        
        unique_results = []
        seen_content = set()
        
        for result in results:
            content = result.get('content', '')
            title = result.get('title', '')
            
            # Create content signature
            signature = (content[:100] + title).lower().replace(' ', '')
            
            if signature not in seen_content and len(signature) > 10:
                seen_content.add(signature)
                unique_results.append(result)
        
        return unique_results
    
    async def _rerank_results(self, results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Rerank results considering source diversity and relevance"""
        if not results:
            return results
        
        # Calculate rerank scores
        for result in results:
            base_score = result.get('score', 0.0)
            
            # Source diversity bonus
            source_bonus = 0.1 if result.get('source') == 'web_search' else 0.0
            
            # Recency bonus for web results
            recency_bonus = 0.05 if result.get('source') == 'web_search' else 0.0
            
            # Final rerank score
            result['rerank_score'] = base_score + source_bonus + recency_bonus
        
        # Sort by rerank score
        reranked = sorted(results, key=lambda x: x.get('rerank_score', 0.0), reverse=True)
        
        return reranked