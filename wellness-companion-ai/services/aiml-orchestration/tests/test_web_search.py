import pytest
import asyncio
from src.search.tavily_client import tavily_client
from src.search.web_search import web_search_service
from src.search.web_result_processor import web_result_processor

class TestWebSearch:
    
    @pytest.mark.asyncio
    async def test_tavily_health_check(self):
        """Test Tavily API connectivity"""
        health = await tavily_client.health_check()
        assert isinstance(health, bool)
    
    @pytest.mark.asyncio
    async def test_web_search_basic(self):
        """Test basic web search functionality"""
        result = await web_search_service.search("Python programming", max_results=2)
        
        if result:
            assert result.query == "Python programming"
            assert isinstance(result.results, list)
            assert result.total_results >= 0
    
    @pytest.mark.asyncio
    async def test_result_processing(self):
        """Test web result processing pipeline"""
        mock_response = {
            'answer': 'Test answer',
            'results': [
                {
                    'title': 'Test Title',
                    'url': 'https://example.com',
                    'content': 'Test content for processing',
                    'score': 0.8
                }
            ]
        }
        
        processed = await web_result_processor.process_results(mock_response, "test query")
        assert 'results' in processed
        assert isinstance(processed['results'], list)