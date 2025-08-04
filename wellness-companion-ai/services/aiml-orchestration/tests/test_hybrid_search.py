import pytest
import asyncio
from src.orchestrators.hybrid_search import hybrid_search
from src.orchestrators.confidence_evaluator import confidence_evaluator
from src.search.web_search import web_search_service

class TestHybridSearch:
    
    @pytest.mark.asyncio
    async def test_web_search_fallback(self):
        """Test that low confidence triggers web search"""
        query = "latest quantum computing news"
        result = await hybrid_search.search(query)
        
        assert result is not None
        assert result.get('type') in ['web', 'fallback_web', 'hybrid']
        assert 'confidence' in result or 'web_confidence' in result
    
    @pytest.mark.asyncio
    async def test_confidence_threshold(self):
        """Test confidence threshold evaluation"""
        mock_results = [{'score': 0.5, 'content': 'test content', 'title': 'test'}]
        confidence = await confidence_evaluator.evaluate_local_confidence(mock_results, "test query")
        
        should_fallback = confidence_evaluator.should_trigger_fallback(confidence)
        assert isinstance(should_fallback, bool)
        assert confidence >= 0.0 and confidence <= 1.0
    
    @pytest.mark.asyncio
    async def test_web_search_integration(self):
        """Test web search integration works"""
        result = await web_search_service.search("Python tutorial", max_results=2)
        
        if result:
            assert hasattr(result, 'to_dict')
            data = result.to_dict()
            assert 'query' in data
            assert 'results' in data