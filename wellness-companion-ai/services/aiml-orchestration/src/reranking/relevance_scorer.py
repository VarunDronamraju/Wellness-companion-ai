
# File: services/aiml-orchestration/src/reranking/relevance_scorer.py
"""
Relevance Scorer - Score relevance across different result types
Location: services/aiml-orchestration/src/reranking/relevance_scorer.py
"""

import logging
from typing import Dict, List, Optional, Any
import re

logger = logging.getLogger(__name__)

class RelevanceScorer:
    """Scores relevance across different result types"""
    
    def __init__(self):
        self.local_weight = 0.7
        self.web_weight = 0.3
        
    async def score_relevance(
        self, 
        results: List[Dict[str, Any]], 
        query: str
    ) -> List[Dict[str, Any]]:
        """Score relevance for all results"""
        try:
            scored_results = []
            
            for result in results:
                relevance_score = await self._calculate_relevance_score(result, query)
                result_copy = result.copy()
                result_copy['relevance_score'] = relevance_score
                scored_results.append(result_copy)
            
            return scored_results
            
        except Exception as e:
            logger.error(f"Relevance scoring error: {e}")
            return results
    
    async def _calculate_relevance_score(self, result: Dict[str, Any], query: str) -> float:
        """Calculate relevance score for a single result"""
        content = result.get('content', '')
        title = result.get('title', '')
        
        # Extract query terms
        query_terms = re.findall(r'\b\w+\b', query.lower())
        
        # Calculate term frequency in content and title
        content_lower = content.lower()
        title_lower = title.lower()
        
        content_score = 0.0
        title_score = 0.0
        
        for term in query_terms:
            # Content matches
            content_matches = content_lower.count(term)
            content_score += min(content_matches * 0.1, 0.5)
            
            # Title matches (higher weight)
            title_matches = title_lower.count(term)
            title_score += min(title_matches * 0.3, 0.8)
        
        # Combine scores
        total_score = (content_score * 0.6) + (title_score * 0.4)
        
        # Apply source weight
        source_type = result.get('result_source', 'unknown')
        if source_type == 'local':
            total_score *= self.local_weight
        elif source_type == 'web':
            total_score *= self.web_weight
        
        return min(total_score, 1.0)