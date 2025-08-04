# ==== FILE 1: services/aiml-orchestration/src/search/web_search.py ====

"""
Main web search interface using Tavily API.
Entry point for all web search operations.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import sys

sys.path.append('/app/src')

from .tavily_client import TavilyClient
from .web_search_config import WebSearchConfig
from .search_request_builder import SearchRequestBuilder

logger = logging.getLogger(__name__)

@dataclass
class WebSearchResult:
    """Web search result with metadata."""
    query: str
    results: List[Dict[str, Any]]
    total_results: int
    search_time: float
    confidence: float
    sources: List[str]
    metadata: Dict[str, Any]

class WebSearchClient:
    """
    Main web search client interface.
    Handles all web search operations using Tavily API.
    """
    
    def __init__(self, config: Optional[WebSearchConfig] = None):
        self.config = config or WebSearchConfig()
        self.tavily_client = TavilyClient(self.config)
        self.request_builder = SearchRequestBuilder(self.config)
        
        self.search_stats = {
            'total_searches': 0,
            'successful_searches': 0,
            'failed_searches': 0,
            'average_search_time': 0.0,
            'total_search_time': 0.0,
            'api_calls_made': 0,
            'rate_limit_hits': 0
        }

    async def search(
        self,
        query: str,
        max_results: int = 10,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        search_depth: str = "basic"
    ) -> WebSearchResult:
        """
        Perform web search using Tavily API.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            include_domains: List of domains to include in search
            exclude_domains: List of domains to exclude from search
            search_depth: Search depth ("basic" or "advanced")
            
        Returns:
            WebSearchResult with search results and metadata
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"Starting web search for query: {query[:50]}...")
            
            # Build search request
            search_request = self.request_builder.build_request(
                query=query,
                max_results=max_results,
                include_domains=include_domains,
                exclude_domains=exclude_domains,
                search_depth=search_depth
            )
            
            # Perform search using Tavily client
            tavily_results = await self.tavily_client.search(search_request)
            
            if not tavily_results.get('success', False):
                raise Exception(f"Tavily search failed: {tavily_results.get('error', 'Unknown error')}")
            
            # Process results
            processed_results = self._process_search_results(tavily_results)
            
            # Calculate metrics
            search_time = (datetime.now() - start_time).total_seconds()
            confidence = self._calculate_search_confidence(processed_results)
            sources = self._extract_sources(processed_results)
            
            web_search_result = WebSearchResult(
                query=query,
                results=processed_results,
                total_results=len(processed_results),
                search_time=search_time,
                confidence=confidence,
                sources=sources,
                metadata={
                    'timestamp': datetime.now().isoformat(),
                    'search_depth': search_depth,
                    'max_results_requested': max_results,
                    'include_domains': include_domains,
                    'exclude_domains': exclude_domains,
                    'tavily_response_time': tavily_results.get('response_time', 0)
                }
            )
            
            self._update_stats(True, search_time)
            logger.info(f"Web search completed: {len(processed_results)} results, confidence: {confidence:.2f}")
            
            return web_search_result
            
        except Exception as e:
            search_time = (datetime.now() - start_time).total_seconds()
            self._update_stats(False, search_time)
            logger.error(f"Web search failed: {str(e)}")
            
            return self._create_error_result(query, str(e), search_time)

    async def search_with_context(
        self,
        query: str,
        context: str,
        max_results: int = 10
    ) -> WebSearchResult:
        """
        Perform contextual web search with additional context.
        """
        # Enhance query with context
        enhanced_query = self.request_builder.enhance_query_with_context(query, context)
        
        return await self.search(
            query=enhanced_query,
            max_results=max_results,
            search_depth="advanced"
        )

    async def search_multiple_queries(
        self,
        queries: List[str],
        max_results_per_query: int = 5
    ) -> List[WebSearchResult]:
        """
        Perform multiple web searches concurrently.
        """
        tasks = [
            self.search(query, max_results_per_query)
            for query in queries
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful results
        successful_results = [
            result for result in results
            if isinstance(result, WebSearchResult)
        ]
        
        logger.info(f"Batch web search completed: {len(successful_results)}/{len(queries)} successful")
        return successful_results

    def _process_search_results(self, tavily_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process raw Tavily results into standardized format."""
        processed_results = []
        
        raw_results = tavily_results.get('results', [])
        
        for result in raw_results:
            processed_result = {
                'title': result.get('title', ''),
                'content': result.get('content', ''),
                'url': result.get('url', ''),
                'score': result.get('score', 0.5),
                'published_date': result.get('published_date', ''),
                'source': self._extract_domain(result.get('url', '')),
                'snippet': result.get('snippet', result.get('content', '')[:200]),
                'metadata': {
                    'search_engine': 'tavily',
                    'result_type': 'web',
                    'raw_score': result.get('score', 0.5),
                    'timestamp': datetime.now().isoformat()
                }
            }
            
            # Only add if has meaningful content
            if processed_result['content'].strip() and processed_result['title'].strip():
                processed_results.append(processed_result)
        
        return processed_results

    def _calculate_search_confidence(self, results: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for web search results."""
        if not results:
            return 0.0
        
        # Base confidence
        confidence = 0.5
        
        # Result count factor
        result_count = len(results)
        if result_count >= 5:
            confidence += 0.2
        elif result_count >= 3:
            confidence += 0.1
        
        # Average score factor
        scores = [result.get('score', 0.5) for result in results]
        avg_score = sum(scores) / len(scores) if scores else 0.5
        confidence += avg_score * 0.2
        
        # Content quality factor
        avg_content_length = sum(len(result.get('content', '')) for result in results) / len(results)
        if avg_content_length > 100:
            confidence += 0.1
        
        return min(1.0, confidence)

    def _extract_sources(self, results: List[Dict[str, Any]]) -> List[str]:
        """Extract unique sources from search results."""
        sources = set()
        for result in results:
            source = result.get('source', '')
            if source:
                sources.add(source)
        
        return list(sources)

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.replace('www.', '')
        except Exception:
            return 'unknown'

    def _create_error_result(self, query: str, error: str, search_time: float) -> WebSearchResult:
        """Create error result when search fails."""
        return WebSearchResult(
            query=query,
            results=[],
            total_results=0,
            search_time=search_time,
            confidence=0.0,
            sources=[],
            metadata={
                'error': error,
                'timestamp': datetime.now().isoformat(),
                'search_failed': True
            }
        )

    def _update_stats(self, success: bool, search_time: float):
        """Update search statistics."""
        self.search_stats['total_searches'] += 1
        self.search_stats['api_calls_made'] += 1
        
        if success:
            self.search_stats['successful_searches'] += 1
        else:
            self.search_stats['failed_searches'] += 1
        
        self.search_stats['total_search_time'] += search_time
        self.search_stats['average_search_time'] = (
            self.search_stats['total_search_time'] / 
            self.search_stats['total_searches']
        )

    def get_search_statistics(self) -> Dict[str, Any]:
        """Get web search statistics."""
        return {
            **self.search_stats,
            'success_rate': f"{(self.search_stats['successful_searches'] / max(1, self.search_stats['total_searches'])) * 100:.2f}%",
            'average_results_per_search': self.search_stats['successful_searches'] / max(1, self.search_stats['total_searches'])
        }

    def clear_cache(self):
        """Clear any cached search results."""
        if hasattr(self.tavily_client, 'clear_cache'):
            self.tavily_client.clear_cache()
