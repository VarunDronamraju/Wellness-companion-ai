# services/aiml-orchestration/src/search/web_search_config.py

import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field

class WebSearchConfig(BaseSettings):
    """Configuration for web search services"""
    
    # Tavily API Configuration
    tavily_api_key: str = Field(..., env="TAVILY_API_KEY")
    tavily_base_url: str = Field("https://api.tavily.com", env="TAVILY_BASE_URL")
    tavily_max_results: int = Field(5, env="TAVILY_MAX_RESULTS")
    tavily_search_depth: str = Field("basic", env="TAVILY_SEARCH_DEPTH")
    tavily_include_domains: Optional[str] = Field(None, env="TAVILY_INCLUDE_DOMAINS")
    tavily_exclude_domains: Optional[str] = Field(None, env="TAVILY_EXCLUDE_DOMAINS")
    
    # Search Configuration
    confidence_threshold: float = Field(0.7, env="CONFIDENCE_THRESHOLD")
    web_search_timeout: int = Field(10, env="WEB_SEARCH_TIMEOUT")
    web_search_rate_limit: int = Field(60, env="WEB_SEARCH_RATE_LIMIT")
    cache_web_results: bool = Field(True, env="CACHE_WEB_RESULTS")
    web_cache_ttl: int = Field(3600, env="WEB_CACHE_TTL")
    
    # Feature Flags
    enable_web_search: bool = Field(True, env="ENABLE_WEB_SEARCH")
    web_search_fallback_enabled: bool = Field(True, env="WEB_SEARCH_FALLBACK_ENABLED")
    
    @property
    def include_domains_list(self) -> List[str]:
        """Convert comma-separated domains to list"""
        if not self.tavily_include_domains:
            return []
        return [domain.strip() for domain in self.tavily_include_domains.split(",") if domain.strip()]
    
    @property
    def exclude_domains_list(self) -> List[str]:
        """Convert comma-separated domains to list"""
        if not self.tavily_exclude_domains:
            return []
        return [domain.strip() for domain in self.tavily_exclude_domains.split(",") if domain.strip()]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global configuration instance
web_search_config = WebSearchConfig()