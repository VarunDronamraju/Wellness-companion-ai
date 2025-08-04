# services/aiml-orchestration/src/search/tavily_client.py

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any
from .web_search_config import web_search_config
from .api_rate_limiter import rate_limiter
from .search_request_builder import search_request_builder

logger = logging.getLogger(__name__)

class TavilyAPIError(Exception):
    """Custom exception for Tavily API errors"""
    pass

class TavilyClient:
    """Async client for Tavily API with rate limiting and error handling"""
    
    def __init__(self):
        self.config = web_search_config
        self.base_url = self.config.tavily_base_url
        self.api_key = self.config.tavily_api_key
        self.timeout = self.config.web_search_timeout
        
        # Session will be created when needed
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers=search_request_builder.build_headers()
            )
        return self._session
    
    async def search(
        self,
        query: str,
        max_results: Optional[int] = None,
        search_depth: Optional[str] = None,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        include_raw_content: bool = False
    ) -> Dict[str, Any]:
        """
        Perform web search using Tavily API
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            search_depth: Search depth (basic, advanced)
            include_domains: List of domains to include
            exclude_domains: List of domains to exclude
            include_raw_content: Whether to include raw content
        
        Returns:
            Search results from Tavily API
        
        Raises:
            TavilyAPIError: If API request fails
        """
        
        # Validate query
        if not search_request_builder.validate_query(query):
            raise TavilyAPIError(f"Invalid query: {query}")
        
        # Check rate limits
        await rate_limiter.wait_if_needed()
        
        if not await rate_limiter.can_make_call():
            raise TavilyAPIError("Rate limit exceeded, cannot make API call")
        
        # Build request
        request_data = search_request_builder.build_search_request(
            query=query,
            max_results=max_results,
            search_depth=search_depth,
            include_domains=include_domains,
            exclude_domains=exclude_domains,
            include_raw_content=include_raw_content
        )
        
        # Add API key
        request_data["api_key"] = self.api_key
        
        try:
            # Make API request
            session = await self._get_session()
            
            logger.info(f"Making Tavily API request for query: {query}")
            
            async with session.post(
                f"{self.base_url}/search",
                json=request_data
            ) as response:
                
                # Record the API call
                await rate_limiter.record_call()
                
                # Handle response
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Tavily API request successful. Got {len(result.get('results', []))} results")
                    return result
                
                # Handle API errors
                error_text = await response.text()
                error_msg = f"Tavily API error {response.status}: {error_text}"
                logger.error(error_msg)
                
                if response.status == 401:
                    raise TavilyAPIError("Invalid Tavily API key")
                elif response.status == 429:
                    raise TavilyAPIError("Tavily API rate limit exceeded")
                elif response.status == 400:
                    raise TavilyAPIError(f"Bad request: {error_text}")
                else:
                    raise TavilyAPIError(error_msg)
        
        except asyncio.TimeoutError:
            logger.error(f"Tavily API timeout after {self.timeout} seconds")
            raise TavilyAPIError(f"API request timeout after {self.timeout} seconds")
        
        except aiohttp.ClientError as e:
            logger.error(f"Tavily API client error: {str(e)}")
            raise TavilyAPIError(f"Client error: {str(e)}")
        
        except Exception as e:
            logger.error(f"Unexpected error in Tavily API call: {str(e)}")
            raise TavilyAPIError(f"Unexpected error: {str(e)}")
    
    async def health_check(self) -> bool:
        """Check if Tavily API is accessible"""
        try:
            # Simple test query
            result = await self.search("test", max_results=1)
            return bool(result.get('results'))
        
        except Exception as e:
            logger.error(f"Tavily API health check failed: {str(e)}")
            return False
    
    async def get_api_status(self) -> Dict[str, Any]:
        """Get API status and usage information"""
        rate_usage = rate_limiter.get_current_usage()
        
        return {
            "api_key_configured": bool(self.api_key and self.api_key != "your_tavily_api_key_here"),
            "base_url": self.base_url,
            "timeout": self.timeout,
            "rate_limiting": rate_usage,
            "feature_enabled": self.config.enable_web_search
        }
    
    async def close(self):
        """Close the aiohttp session"""
        if self._session and not self._session.closed:
            await self._session.close()
            logger.debug("Tavily client session closed")

# Global Tavily client instance
tavily_client = TavilyClient()