
# ==== FILE 2: services/aiml-orchestration/src/search/tavily_client.py ====

"""
Tavily API client wrapper with rate limiting and error handling.
Direct integration with Tavily search API.
"""

import logging
import asyncio
import aiohttp
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import time


from .web_search_config import WebSearchConfig
from .api_rate_limiter import APIRateLimiter

logger = logging.getLogger(__name__)

class TavilyClient:
    """
    Tavily API client with rate limiting and error handling.
    """
    
    def __init__(self, config: WebSearchConfig):
        self.config = config
        self.rate_limiter = APIRateLimiter(
            calls_per_minute=config.rate_limit_per_minute,
            calls_per_hour=config.rate_limit_per_hour
        )
        
        self.api_stats = {
            'total_api_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'rate_limited_calls': 0,
            'average_response_time': 0.0,
            'total_response_time': 0.0
        }
        
        # Cache for recent searches (simple in-memory cache)
        self.search_cache = {}
        self.cache_ttl = 300  # 5 minutes

    async def search(self, search_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform search using Tavily API.
        
        Args:
            search_request: Formatted search request
            
        Returns:
            Tavily API response
        """
        start_time = datetime.now()
        
        try:
            # Check cache first
            cache_key = self._get_cache_key(search_request)
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                logger.debug("Returning cached result for search request")
                return cached_result
            
            # Check rate limits
            if not await self.rate_limiter.can_make_request():
                self.api_stats['rate_limited_calls'] += 1
                raise Exception("Rate limit exceeded for Tavily API")
            
            # Make API request
            response = await self._make_api_request(search_request)
            
            # Cache successful response
            if response.get('success', False):
                self._cache_result(cache_key, response)
            
            response_time = (datetime.now() - start_time).total_seconds()
            response['response_time'] = response_time
            
            self._update_stats(True, response_time)
            return response
            
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds()
            self._update_stats(False, response_time)
            logger.error(f"Tavily API request failed: {str(e)}")
            
            return {
                'success': False,
                'error': str(e),
                'response_time': response_time,
                'results': []
            }

    async def _make_api_request(self, search_request: Dict[str, Any]) -> Dict[str, Any]:
        """Make actual HTTP request to Tavily API."""
        
        # Tavily API endpoint
        url = "https://api.tavily.com/search"
        
        # Prepare request payload
        payload = {
            "api_key": self.config.tavily_api_key,
            "query": search_request['query'],
            "search_depth": search_request.get('search_depth', 'basic'),
            "include_answer": True,
            "include_raw_content": False,
            "max_results": search_request.get('max_results', 10),
            "include_domains": search_request.get('include_domains', []),
            "exclude_domains": search_request.get('exclude_domains', [])
        }
        
        # Remove empty lists to avoid API issues
        if not payload["include_domains"]:
            del payload["include_domains"]
        if not payload["exclude_domains"]:
            del payload["exclude_domains"]
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "WellnessCompanionAI/1.0"
        }
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Transform Tavily response to our format
                        return {
                            'success': True,
                            'results': data.get('results', []),
                            'answer': data.get('answer', ''),
                            'query': search_request['query'],
                            'response_metadata': {
                                'status_code': response.status,
                                'tavily_response': data
                            }
                        }
                    
                    elif response.status == 429:
                        # Rate limited
                        self.api_stats['rate_limited_calls'] += 1
                        raise Exception("Tavily API rate limit exceeded")
                    
                    elif response.status == 401:
                        raise Exception("Invalid Tavily API key")
                    
                    else:
                        error_text = await response.text()
                        raise Exception(f"Tavily API error {response.status}: {error_text}")
        
        except aiohttp.ClientError as e:
            raise Exception(f"Network error calling Tavily API: {str(e)}")
        
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON response from Tavily API: {str(e)}")

    def _get_cache_key(self, search_request: Dict[str, Any]) -> str:
        """Generate cache key for search request."""
        key_parts = [
            search_request['query'],
            str(search_request.get('max_results', 10)),
            str(search_request.get('search_depth', 'basic')),
            str(sorted(search_request.get('include_domains', []))),
            str(sorted(search_request.get('exclude_domains', [])))
        ]
        return '|'.join(key_parts)

    def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached result if still valid."""
        if cache_key in self.search_cache:
            cached_entry = self.search_cache[cache_key]
            if datetime.now() - cached_entry['timestamp'] < timedelta(seconds=self.cache_ttl):
                return cached_entry['result']
            else:
                # Remove expired entry
                del self.search_cache[cache_key]
        
        return None

    def _cache_result(self, cache_key: str, result: Dict[str, Any]):
        """Cache search result."""
        self.search_cache[cache_key] = {
            'result': result,
            'timestamp': datetime.now()
        }
        
        # Simple cache cleanup - remove old entries if cache gets too large
        if len(self.search_cache) > 100:
            # Remove oldest 20 entries
            sorted_items = sorted(
                self.search_cache.items(),
                key=lambda x: x[1]['timestamp']
            )
            for cache_key, _ in sorted_items[:20]:
                del self.search_cache[cache_key]

    def _update_stats(self, success: bool, response_time: float):
        """Update API call statistics."""
        self.api_stats['total_api_calls'] += 1
        
        if success:
            self.api_stats['successful_calls'] += 1
        else:
            self.api_stats['failed_calls'] += 1
        
        self.api_stats['total_response_time'] += response_time
        self.api_stats['average_response_time'] = (
            self.api_stats['total_response_time'] / 
            self.api_stats['total_api_calls']
        )

    def get_api_statistics(self) -> Dict[str, Any]:
        """Get Tavily API usage statistics."""
        return {
            **self.api_stats,
            'success_rate': f"{(self.api_stats['successful_calls'] / max(1, self.api_stats['total_api_calls'])) * 100:.2f}%",
            'cache_size': len(self.search_cache),
            'rate_limit_status': self.rate_limiter.get_status()
        }

    def clear_cache(self):
        """Clear search result cache."""
        self.search_cache.clear()
        logger.info("Tavily client cache cleared")

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on Tavily API."""
        try:
            # Simple test search
            test_request = {
                'query': 'test health check',
                'max_results': 1,
                'search_depth': 'basic'
            }
            
            result = await self.search(test_request)
            
            return {
                'healthy': result.get('success', False),
                'response_time': result.get('response_time', 0),
                'error': result.get('error'),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
