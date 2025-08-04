import logging
from typing import Dict, List, Any, Optional
from .search_strategy import SearchStrategy
from .confidence_evaluator import ConfidenceEvaluator
from .fallback_manager import FallbackManager
from .search_coordinator import SearchCoordinator

logger = logging.getLogger(__name__)

class HybridSearch:
    """Main hybrid search orchestrator"""
    
    def __init__(self):
        self.strategy = SearchStrategy()
        self.evaluator = ConfidenceEvaluator()
        self.fallback = FallbackManager()
        self.coordinator = SearchCoordinator()
    
    async def search(
        self,
        query: str,
        user_context: Optional[Dict[str, Any]] = None,
        force_strategy: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute hybrid search with fallback logic"""
        try:
            # Determine search strategy
            strategy = force_strategy or await self.strategy.determine_strategy(query, user_context)
            
            if strategy == "local_only":
                return await self._local_search(query, user_context)
            elif strategy == "web_only":
                return await self._web_search(query)
            else:  # hybrid
                return await self._hybrid_search(query, user_context)
                
        except Exception as e:
            logger.error(f"Hybrid search error: {str(e)}")
            return await self.fallback.emergency_fallback(query)
    
    async def _local_search(self, query: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform local-only search"""
        local_results = await self.coordinator.search_local(query, context)
        confidence = await self.evaluator.evaluate_local_confidence(local_results, query)
        
        if confidence >= 0.7:
            return {"type": "local", "confidence": confidence, "results": local_results}
        else:
            return await self.fallback.trigger_web_fallback(query, local_results, confidence)
    
    async def _web_search(self, query: str) -> Dict[str, Any]:
        """Perform web-only search"""
        web_results = await self.coordinator.search_web(query)
        return {"type": "web", "confidence": 0.8, "results": web_results}
    
    async def _hybrid_search(self, query: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform combined local + web search"""
        local_results = await self.coordinator.search_local(query, context)
        local_confidence = await self.evaluator.evaluate_local_confidence(local_results, query)
        
        if local_confidence >= 0.7:
            return {"type": "local", "confidence": local_confidence, "results": local_results}
        
        # Trigger web search fallback
        web_results = await self.coordinator.search_web(query)
        combined_results = await self.coordinator.combine_results(local_results, web_results, query)
        
        return {
            "type": "hybrid",
            "local_confidence": local_confidence,
            "web_confidence": 0.8,
            "combined_confidence": 0.85,
            "results": combined_results
        }

hybrid_search = HybridSearch()