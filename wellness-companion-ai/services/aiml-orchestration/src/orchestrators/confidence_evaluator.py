import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class ConfidenceEvaluator:
    """Enhanced confidence evaluation for search results"""
    
    def __init__(self):
        self.confidence_threshold = 0.7
    
    async def evaluate_local_confidence(
        self, 
        results: List[Dict[str, Any]], 
        query: str
    ) -> float:
        """Evaluate confidence in local search results"""
        if not results:
            return 0.0
        
        # Get top result confidence
        top_score = max((r.get('score', 0) for r in results), default=0)
        
        # Calculate result count factor
        result_count_factor = min(len(results) / 5.0, 1.0)
        
        # Calculate query match factor
        query_match_factor = self._calculate_query_match(results[0], query)
        
        # Combined confidence score
        confidence = (top_score * 0.5) + (result_count_factor * 0.3) + (query_match_factor * 0.2)
        
        logger.debug(f"Local confidence: {confidence:.3f} (score:{top_score:.3f}, count:{result_count_factor:.3f}, match:{query_match_factor:.3f})")
        return min(confidence, 1.0)
    
    def _calculate_query_match(self, result: Dict[str, Any], query: str) -> float:
        """Calculate how well result matches query"""
        content = result.get('content', '').lower()
        title = result.get('title', '').lower()
        query_words = query.lower().split()
        
        if not query_words:
            return 0.0
        
        title_matches = sum(1 for word in query_words if word in title) / len(query_words)
        content_matches = sum(1 for word in query_words if word in content) / len(query_words)
        
        return (title_matches * 0.7) + (content_matches * 0.3)
    
    def should_trigger_fallback(self, confidence: float) -> bool:
        """Check if confidence is below threshold for fallback"""
        return confidence < self.confidence_threshold

confidence_evaluator = ConfidenceEvaluator()