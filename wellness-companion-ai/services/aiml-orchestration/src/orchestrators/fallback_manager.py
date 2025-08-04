import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class FallbackManager:
    """Manage search fallback strategies"""
    
    async def trigger_web_fallback(
        self, 
        query: str, 
        local_results: List[Dict[str, Any]], 
        local_confidence: float
    ) -> Dict[str, Any]:
        """Trigger web search when local confidence is low"""
        logger.info(f"Triggering web fallback for query: {query} (confidence: {local_confidence:.3f})")
        
        try:
            from search.web_search import web_search_service
            
            # Perform web search
            web_response = await web_search_service.search(query, max_results=5)
            
            if web_response:
                return {
                    "type": "fallback_web",
                    "local_confidence": local_confidence,
                    "web_confidence": 0.8,
                    "trigger_reason": f"Local confidence {local_confidence:.3f} below threshold 0.7",
                    "results": web_response.to_dict()
                }
            else:
                return await self.emergency_fallback(query)
                
        except Exception as e:
            logger.error(f"Web fallback failed: {str(e)}")
            return await self.emergency_fallback(query)
    
    async def emergency_fallback(self, query: str) -> Dict[str, Any]:
        """Emergency fallback when all search methods fail"""
        logger.warning(f"Emergency fallback activated for query: {query}")
        
        return {
            "type": "emergency_fallback",
            "confidence": 0.1,
            "message": "Search temporarily unavailable. Please try again later.",
            "results": {
                "answer": "I'm currently unable to search for information. Please try again in a moment.",
                "results": [],
                "total_results": 0
            }
        }

fallback_manager = FallbackManager()