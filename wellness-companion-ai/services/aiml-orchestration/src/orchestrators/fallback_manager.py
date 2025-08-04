
# File: services/aiml-orchestration/src/orchestrators/fallback_manager.py
"""
Fallback Manager - Manage fallback to web search
Location: services/aiml-orchestration/src/orchestrators/fallback_manager.py
"""
import os
import asyncio
import logging
from typing import Dict, List, Optional, Any

from src.search.web_search import WebSearchClient
from src.search.web_result_processor import WebResultProcessor

logger = logging.getLogger(__name__)

class FallbackManager:
    """Manages fallback to web search when local results are insufficient"""
    
    def __init__(self):
        from src.search.web_search import WebSearchConfig
        config = WebSearchConfig(os.getenv('TAVILY_API_KEY', ''))
        self.web_client = WebSearchClient(config)
        self.web_processor = WebResultProcessor()
        self.max_retries = 2
        
    async def execute_web_fallback(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Execute web search fallback with retry logic"""
        try:
            logger.info(f"Executing web search fallback for query: {query}")
            
            # Perform web search
            web_response = await self.web_client.search(query, max_results)
            
            if not web_response or not web_response.get('results'):
                logger.warning("No web search results returned")
                return []
            
            # Process web results
            processed_results = await self.web_processor.process_web_results(web_response, query)
            
            # Convert to dict format for compatibility
            formatted_results = []
            for result in processed_results:
                formatted_results.append({
                    'content': result.content,
                    'title': result.title,
                    'url': result.url,
                    'score': result.confidence_score,
                    'source': 'web_search',
                    'metadata': result.metadata,
                    'chunks': result.chunks
                })
            
            logger.info(f"Web fallback returned {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Web fallback error: {e}")
            return []
    
    async def should_fallback(self, confidence: float, threshold: float) -> bool:
        """Determine if fallback should be triggered"""
        return confidence < threshold