# services/aiml-orchestration/src/search/search_request_builder.py

from typing import Dict, List, Optional, Any
import re
import logging
from .web_search_config import web_search_config

logger = logging.getLogger(__name__)

class SearchRequestBuilder:
    """Build optimized search requests for Tavily API"""
    
    def __init__(self):
        self.config = web_search_config
    
    def build_search_request(
        self,
        query: str,
        max_results: Optional[int] = None,
        search_depth: Optional[str] = None,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        include_raw_content: bool = False,
        include_images: bool = False
    ) -> Dict[str, Any]:
        """Build a complete search request for Tavily API"""
        
        # Optimize the query
        optimized_query = self._optimize_query(query)
        
        # Build request parameters
        request_params = {
            "query": optimized_query,
            "search_depth": search_depth or self.config.tavily_search_depth,
            "max_results": max_results or self.config.tavily_max_results,
            "include_raw_content": include_raw_content,
            "include_images": include_images,
            "include_answer": True,  # Get AI-generated answer
            "format": "json"
        }
        
        # Add domain filters
        domains_config = self._build_domain_filters(include_domains, exclude_domains)
        if domains_config:
            request_params.update(domains_config)
        
        logger.debug(f"Built search request: {request_params}")
        return request_params
    
    def _optimize_query(self, query: str) -> str:
        """Optimize query for better web search results"""
        # Remove excessive whitespace
        query = ' '.join(query.split())
        
        # Remove quotes that might interfere with search
        query = query.replace('"', '').replace("'", "")
        
        # Limit query length (Tavily works best with concise queries)
        if len(query) > 200:
            query = query[:200].rsplit(' ', 1)[0]  # Cut at word boundary
            logger.info(f"Query truncated to: {query}")
        
        # Add context keywords for better results
        query = self._add_context_keywords(query)
        
        return query
    
    def _add_context_keywords(self, query: str) -> str:
        """Add relevant context keywords to improve search results"""
        # Define context patterns and their keywords
        context_patterns = {
            r'\b(code|programming|development|software)\b': 'programming tutorial',
            r'\b(health|medical|disease|symptoms)\b': 'health information',
            r'\b(recipe|cooking|ingredients)\b': 'recipe cooking',
            r'\b(news|current|recent|latest)\b': 'news latest',
            r'\b(how to|tutorial|guide|step)\b': 'tutorial guide'
        }
        
        # Check if query needs context enhancement
        query_lower = query.lower()
        for pattern, context in context_patterns.items():
            if re.search(pattern, query_lower) and context not in query_lower:
                # Only add if query is short enough
                if len(query) + len(context) + 1 <= 200:
                    query = f"{query} {context}"
                break
        
        return query
    
    def _build_domain_filters(
        self,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None
    ) -> Dict[str, List[str]]:
        """Build domain filter configuration"""
        filters = {}
        
        # Use provided domains or config defaults
        include = include_domains or self.config.include_domains_list
        exclude = exclude_domains or self.config.exclude_domains_list
        
        if include:
            filters["include_domains"] = include
            logger.debug(f"Including domains: {include}")
        
        if exclude:
            filters["exclude_domains"] = exclude
            logger.debug(f"Excluding domains: {exclude}")
        
        return filters
    
    def build_headers(self) -> Dict[str, str]:
        """Build HTTP headers for Tavily API requests"""
        return {
            "Content-Type": "application/json",
            "User-Agent": "WellnessCompanionAI/1.0",
            "Accept": "application/json"
        }
    
    def validate_query(self, query: str) -> bool:
        """Validate if query is suitable for web search"""
        if not query or not query.strip():
            logger.warning("Empty query provided")
            return False
        
        # Check minimum length
        if len(query.strip()) < 3:
            logger.warning(f"Query too short: {query}")
            return False
        
        # Check for common non-searchable patterns
        non_searchable_patterns = [
            r'^[0-9\s\+\-\*/\(\)]+$',  # Pure math expressions
            r'^[^\w\s]+$',  # Only special characters
        ]
        
        for pattern in non_searchable_patterns:
            if re.match(pattern, query.strip()):
                logger.warning(f"Query not suitable for web search: {query}")
                return False
        
        return True

# Global request builder instance
search_request_builder = SearchRequestBuilder()