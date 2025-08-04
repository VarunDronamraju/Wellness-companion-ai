
# File: services/aiml-orchestration/src/orchestrators/confidence_evaluator.py
"""
Confidence Evaluator - Evaluate confidence scores for search results
Location: services/aiml-orchestration/src/orchestrators/confidence_evaluator.py
"""

import logging
import statistics
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class ConfidenceEvaluator:
    """Evaluates confidence in search results to determine fallback necessity"""
    
    def __init__(self):
        self.min_results_threshold = 3
        self.min_score_threshold = 0.5
        
    async def evaluate_confidence(self, results: List[Dict[str, Any]], query: str) -> float:
        """Evaluate overall confidence in search results"""
        try:
            if not results:
                return 0.0
            
            # Factor 1: Number of results
            result_count_score = min(len(results) / self.min_results_threshold, 1.0)
            
            # Factor 2: Average similarity score
            scores = [r.get('score', 0.0) for r in results]
            avg_score = statistics.mean(scores) if scores else 0.0
            
            # Factor 3: Score distribution (consistency)
            score_std = statistics.stdev(scores) if len(scores) > 1 else 0.0
            consistency_score = 1.0 - min(score_std, 1.0)
            
            # Factor 4: Top result quality
            top_score = max(scores) if scores else 0.0
            
            # Factor 5: Query coverage
            coverage_score = await self._evaluate_query_coverage(results, query)
            
            # Weighted combination
            confidence = (
                result_count_score * 0.2 +
                avg_score * 0.3 +
                consistency_score * 0.1 +
                top_score * 0.2 +
                coverage_score * 0.2
            )
            
            return min(confidence, 1.0)
            
        except Exception as e:
            logger.error(f"Confidence evaluation error: {e}")
            return 0.0
    
    async def _evaluate_query_coverage(self, results: List[Dict[str, Any]], query: str) -> float:
        """Evaluate how well results cover the query"""
        if not results or not query:
            return 0.0
        
        query_terms = set(query.lower().split())
        
        covered_terms = set()
        for result in results:
            content = result.get('content', '') + ' ' + result.get('title', '')
            content_terms = set(content.lower().split())
            covered_terms.update(query_terms.intersection(content_terms))
        
        coverage = len(covered_terms) / len(query_terms) if query_terms else 0.0
        return coverage