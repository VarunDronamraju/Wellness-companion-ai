"""
Web search module for Wellness Companion AI

This module provides web search capabilities using Tavily API with:
- Rate limiting and error handling
- Query optimization and validation
- Structured result processing
- Multiple search types (quick, detailed, news, academic)
"""

from .web_search import web_search_service, WebSearchService, WebSearchResponse, WebSearchResult
from .tavily_client import tavily_client, TavilyClient, TavilyAPIError
from .web_search_config import web_search_config, WebSearchConfig
from .api_rate_limiter import rate_limiter, APIRateLimiter
from .search_request_builder import search_request_builder, SearchRequestBuilder
from .web_result_processor import web_result_processor
from .result_parser import result_parser
from .content_extractor import content_extractor
from .result_validator import result_validator
from .metadata_enricher import metadata_enricher

__all__ = [
    # Main service
    'web_search_service',
    'WebSearchService',
    'WebSearchResponse', 
    'WebSearchResult',
    
    # API client
    'tavily_client',
    'TavilyClient',
    'TavilyAPIError',
    
    # Configuration
    'web_search_config',
    'WebSearchConfig',
    
    # Rate limiting
    'rate_limiter',
    'APIRateLimiter',
    
    # Request building
    'search_request_builder',
    'SearchRequestBuilder',
    
    # Processing pipeline
    'web_result_processor',
    'result_parser',
    'content_extractor',
    'result_validator',
    'metadata_enricher'
]