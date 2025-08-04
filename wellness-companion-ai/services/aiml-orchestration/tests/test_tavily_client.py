
# File: services/aiml-orchestration/tests/test_tavily_client.py
"""
Test Tavily Client - Test Tavily API client
Location: services/aiml-orchestration/tests/test_tavily_client.py
"""

import asyncio
from src.search.tavily_client import TavilyClient
from src.search.web_search import WebSearchConfig

class TestTavilyClient:
    """Test Tavily API client"""
    
    def __init__(self):
        self.config = WebSearchConfig('test-key')
        self.client = TavilyClient(self.config)
    
    async def test_tavily_client_init(self):
        """Test Tavily client initialization"""
        assert self.client.config.api_key == 'test-key'
    
    async def test_query_formatting(self):
        """Test query formatting for Tavily API"""
        query = 'machine learning algorithms'
        formatted = query.strip()
        assert len(formatted) > 0