# File: services/aiml-orchestration/src/orchestrators/hybrid_search.py
"""
Hybrid Search - Main hybrid search orchestrator
Location: services/aiml-orchestration/src/orchestrators/hybrid_search.py
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .search_strategy import SearchStrategy
from .confidence_evaluator import ConfidenceEvaluator
from .fallback_manager import FallbackManager
from .search_coordinator import SearchCoordinator
from src.search.vector_search import VectorSearch
from src.search.web_result_processor import WebResultProcessor

logger = logging.getLogger(__name__)

class HybridSearch:
    """Main orchestrator for hybrid search combining local vector search with web search fallback"""
    
    def __init__(self):
        self.search_strategy = SearchStrategy()
        self.confidence_evaluator = ConfidenceEvaluator()
        self.fallback_manager = FallbackManager()
        self.search_coordinator = SearchCoordinator()
        self.vector_search = VectorSearch()
        self.web_processor = WebResultProcessor()
        
        self.confidence_threshold = 0.7
        
    async def search(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Execute hybrid search with confidence-based fallback"""
        try:
            # Get search strategy
            strategy = await self.search_strategy.determine_strategy(query)
            
            # Perform vector search first
            vector_results = await self.vector_search.search(query, max_results)
            
            # Evaluate confidence
            confidence = await self.confidence_evaluator.evaluate_confidence(vector_results, query)
            
            # Decide on fallback
            if confidence < self.confidence_threshold:
                # Trigger web search fallback
                web_results = await self.fallback_manager.execute_web_fallback(query, max_results)
                
                # Coordinate results
                combined_results = await self.search_coordinator.coordinate_results(
                    vector_results, web_results, query
                )
                
                return {
                    'results': combined_results,
                    'search_type': 'hybrid',
                    'confidence': confidence,
                    'fallback_triggered': True,
                    'strategy': strategy
                }
            else:
                return {
                    'results': vector_results,
                    'search_type': 'vector_only',
                    'confidence': confidence,
                    'fallback_triggered': False,
                    'strategy': strategy
                }
                
        except Exception as e:
            logger.error(f"Hybrid search error: {e}")
            return {'results': [], 'error': str(e)}