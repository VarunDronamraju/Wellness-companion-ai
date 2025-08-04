
# ==== FILE 3: services/aiml-orchestration/src/search/web_search_config.py ====

"""
Web search configuration management.
Centralized configuration for all web search operations.
"""

import os
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class WebSearchConfig:
    """Configuration for web search operations."""
    
    # Tavily API Configuration
    tavily_api_key: str
    tavily_base_url: str = "https://api.tavily.com"
    
    # Rate Limiting
    rate_limit_per_minute: int = 50
    rate_limit_per_hour: int = 1000
    
    # Search Parameters
    default_max_results: int = 10
    max_search_results: int = 20
    default_search_depth: str = "basic"  # "basic" or "advanced"
    
    # Content Filtering
    min_content_length: int = 50
    max_content_length: int = 2000
    excluded_domains: List[str] = None
    preferred_domains: List[str] = None
    
    # Timeout Settings
    request_timeout: int = 30
    connection_timeout: int = 10
    
    # Cache Settings
    enable_caching: bool = True
    cache_ttl_seconds: int = 300  # 5 minutes
    max_cache_size: int = 100
    
    # Quality Thresholds
    min_result_score: float = 0.3
    min_confidence_threshold: float = 0.5
    
    # Response Settings
    include_snippets: bool = True
    include_metadata: bool = True
    include_timestamps: bool = True
    
    def __post_init__(self):
        """Initialize default values and validate configuration."""
        if self.excluded_domains is None:
            self.excluded_domains = [
                'spam-site.com',
                'low-quality-content.net'
            ]
        
        if self.preferred_domains is None:
            self.preferred_domains = [
                'wikipedia.org',
                'britannica.com',
                'nytimes.com',
                'reuters.com',
                'bbc.com'
            ]
        
        # Validate API key
        if not self.tavily_api_key:
            raise ValueError("Tavily API key is required")
        
        # Validate rate limits
        if self.rate_limit_per_minute <= 0 or self.rate_limit_per_hour <= 0:
            raise ValueError("Rate limits must be positive")
        
        # Validate search parameters
        if self.default_max_results <= 0 or self.max_search_results <= 0:
            raise ValueError("Max results must be positive")
        
        if self.default_search_depth not in ["basic", "advanced"]:
            raise ValueError("Search depth must be 'basic' or 'advanced'")

    @classmethod
    def from_environment(cls) -> 'WebSearchConfig':
        """Create configuration from environment variables."""
        tavily_api_key = os.getenv('TAVILY_API_KEY')
        if not tavily_api_key:
            raise ValueError("TAVILY_API_KEY environment variable is required")
        
        return cls(
            tavily_api_key=tavily_api_key,
            tavily_base_url=os.getenv('TAVILY_BASE_URL', 'https://api.tavily.com'),
            rate_limit_per_minute=int(os.getenv('TAVILY_RATE_LIMIT_PER_MINUTE', '50')),
            rate_limit_per_hour=int(os.getenv('TAVILY_RATE_LIMIT_PER_HOUR', '1000')),
            default_max_results=int(os.getenv('WEB_SEARCH_MAX_RESULTS', '10')),
            max_search_results=int(os.getenv('WEB_SEARCH_MAX_LIMIT', '20')),
            default_search_depth=os.getenv('WEB_SEARCH_DEPTH', 'basic'),
            request_timeout=int(os.getenv('WEB_SEARCH_TIMEOUT', '30')),
            enable_caching=os.getenv('WEB_SEARCH_CACHE_ENABLED', 'true').lower() == 'true',
            cache_ttl_seconds=int(os.getenv('WEB_SEARCH_CACHE_TTL', '300'))
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'tavily_api_key': '***masked***',  # Don't expose API key
            'tavily_base_url': self.tavily_base_url,
            'rate_limit_per_minute': self.rate_limit_per_minute,
            'rate_limit_per_hour': self.rate_limit_per_hour,
            'default_max_results': self.default_max_results,
            'max_search_results': self.max_search_results,
            'default_search_depth': self.default_search_depth,
            'min_content_length': self.min_content_length,
            'max_content_length': self.max_content_length,
            'excluded_domains': self.excluded_domains,
            'preferred_domains': self.preferred_domains,
            'request_timeout': self.request_timeout,
            'connection_timeout': self.connection_timeout,
            'enable_caching': self.enable_caching,
            'cache_ttl_seconds': self.cache_ttl_seconds,
            'max_cache_size': self.max_cache_size,
            'min_result_score': self.min_result_score,
            'min_confidence_threshold': self.min_confidence_threshold,
            'include_snippets': self.include_snippets,
            'include_metadata': self.include_metadata,
            'include_timestamps': self.include_timestamps
        }

    def validate(self) -> List[str]:
        """Validate configuration and return list of issues."""
        issues = []
        
        if not self.tavily_api_key:
            issues.append("Tavily API key is missing")
        
        if self.rate_limit_per_minute > self.rate_limit_per_hour:
            issues.append("Per-minute rate limit cannot exceed per-hour rate limit")
        
        if self.default_max_results > self.max_search_results:
            issues.append("Default max results cannot exceed maximum search results")
        
        if self.min_content_length >= self.max_content_length:
            issues.append("Minimum content length must be less than maximum content length")
        
        if self.min_result_score < 0 or self.min_result_score > 1:
            issues.append("Minimum result score must be between 0 and 1")
        
        if self.min_confidence_threshold < 0 or self.min_confidence_threshold > 1:
            issues.append("Minimum confidence threshold must be between 0 and 1")
        
        return issues

    def update(self, **kwargs):
        """Update configuration with new values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(f"Unknown configuration parameter: {key}")

