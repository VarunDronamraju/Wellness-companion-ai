# services/aiml-orchestration/src/search/web_search.py
import logging
from typing import Dict, List, Optional, Any, Union
from .tavily_client import tavily_client, TavilyAPIError
from .web_search_config import web_search_config
from .web_result_processor import web_result_processor


logger = logging.getLogger(__name__)

class WebSearchResult:
    """Structured web search result"""
    
    def __init__(self, data: Dict[str, Any]):
        self.title = data.get('title', '')
        self.url = data.get('url', '')
        self.content = data.get('content', '')
        self.score = data.get('score', 0.0)
        self.published_date = data.get('published_date')
        self.raw_content = data.get('raw_content')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'title': self.title,
            'url': self.url,
            'content': self.content,
            'score': self.score,
            'published_date': self.published_date,
            'raw_content': self.raw_content
        }

from .web_result_processor import web_result_processor  # ← ADD THIS AFTER LINE 5

class WebSearchResponse:
    def __init__(self, tavily_response: Dict[str, Any], query: str):
        self.query = query
        # Process results through pipeline
        processed = web_result_processor.process_results(tavily_response, query)
        
        self.answer = processed.get('answer', '')
        self.results = [WebSearchResult(result) for result in processed.get('results', [])]
        self.total_results = len(self.results)
        self.follow_up_questions = processed.get('follow_up_questions', [])
        self.images = processed.get('images', [])
        self.search_metadata = processed.get('query_metadata', {})

    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'query': self.query,
            'answer': self.answer,
            'results': [result.to_dict() for result in self.results],
            'total_results': self.total_results,
            'follow_up_questions': self.follow_up_questions,
            'images': self.images,
            'metadata': self.search_metadata
        }

class WebSearchService:
    """Main web search service interface"""
    
    def __init__(self):
        self.config = web_search_config
        self.client = tavily_client
    
    async def search(
        self,
        query: str,
        max_results: Optional[int] = None,
        search_depth: str = "basic",
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        include_raw_content: bool = False
    ) -> Optional[WebSearchResponse]:
        """
        Perform web search with error handling
        
        Args:
            query: Search query
            max_results: Maximum results to return
            search_depth: Search depth (basic/advanced)
            include_domains: Domains to include
            exclude_domains: Domains to exclude  
            include_raw_content: Include raw HTML content
        
        Returns:
            WebSearchResponse or None if search fails
        """
        
        # Check if web search is enabled
        if not self.config.enable_web_search:
            logger.warning("Web search is disabled in configuration")
            return None
        
        try:
            logger.info(f"Starting web search for query: {query}")
            
            # Perform search
            tavily_response = await self.client.search(
                query=query,
                max_results=max_results,
                search_depth=search_depth,
                include_domains=include_domains,
                exclude_domains=exclude_domains,
                include_raw_content=include_raw_content
            )
            
            # Process response
            search_response = WebSearchResponse(tavily_response, query)
            
            logger.info(f"Web search completed. Found {search_response.total_results} results")
            return search_response
        
        except TavilyAPIError as e:
            logger.error(f"Tavily API error during search: {str(e)}")
            return None
        
        except Exception as e:
            logger.error(f"Unexpected error during web search: {str(e)}")
            return None
    
    async def quick_search(self, query: str, max_results: int = 3) -> Optional[WebSearchResponse]:
        """Perform a quick web search with minimal results"""
        return await self.search(
            query=query,
            max_results=max_results,
            search_depth="basic",
            include_raw_content=False
        )
    
    async def detailed_search(self, query: str, max_results: int = 10) -> Optional[WebSearchResponse]:
        """Perform a detailed web search with more comprehensive results"""
        return await self.search(
            query=query,
            max_results=max_results,
            search_depth="advanced",
            include_raw_content=True
        )
    
    async def domain_specific_search(
        self, 
        query: str, 
        domains: List[str], 
        max_results: int = 5
    ) -> Optional[WebSearchResponse]:
        """Search within specific domains only"""
        return await self.search(
            query=query,
            max_results=max_results,
            include_domains=domains,
            search_depth="basic"
        )
    
    async def news_search(self, query: str, max_results: int = 5) -> Optional[WebSearchResponse]:
        """Search for news articles"""
        news_domains = [
            "bbc.com", "reuters.com", "cnn.com", "npr.org", 
            "theguardian.com", "nytimes.com", "wsj.com"
        ]
        
        # Add news context to query
        news_query = f"{query} news latest"
        
        return await self.search(
            query=news_query,
            max_results=max_results,
            include_domains=news_domains,
            search_depth="basic"
        )
    
    async def academic_search(self, query: str, max_results: int = 5) -> Optional[WebSearchResponse]:
        """Search for academic content"""
        academic_domains = [
            "scholar.google.com", "arxiv.org", "pubmed.ncbi.nlm.nih.gov",
            "ieee.org", "acm.org", "springer.com", "sciencedirect.com"
        ]
        
        # Add academic context to query
        academic_query = f"{query} research study academic"
        
        return await self.search(
            query=academic_query,
            max_results=max_results,
            include_domains=academic_domains,
            search_depth="advanced"
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """Check web search service health"""
        try:
            # Test API connectivity
            api_healthy = await self.client.health_check()
            
            # Get API status
            api_status = await self.client.get_api_status()
            
            return {
                "service_enabled": self.config.enable_web_search,
                "api_healthy": api_healthy,
                "api_status": api_status,
                "fallback_enabled": self.config.web_search_fallback_enabled,
                "confidence_threshold": self.config.confidence_threshold
            }
        
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "service_enabled": False,
                "api_healthy": False,
                "error": str(e)
            }
    
    async def get_search_suggestions(self, partial_query: str) -> List[str]:
        """Get search suggestions based on partial query"""
        # For now, return basic suggestions
        # This could be enhanced with ML-based suggestions later
        
        suggestions = []
        
        # Add common search patterns
        if len(partial_query) >= 3:
            suggestions.extend([
                f"{partial_query} how to",
                f"{partial_query} tutorial",
                f"{partial_query} guide",
                f"{partial_query} examples",
                f"what is {partial_query}"
            ])
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.client.close()
        logger.info("Web search service cleaned up")

# Global web search service instance
web_search_service = WebSearchService()