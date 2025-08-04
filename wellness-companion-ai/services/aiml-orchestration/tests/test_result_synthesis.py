import pytest
import asyncio
from src.orchestrators.result_synthesizer import result_synthesizer
from src.orchestrators.result_merger import result_merger

class TestResultSynthesis:
    
    @pytest.mark.asyncio
    async def test_result_synthesis_pipeline(self):
        """Test complete result synthesis pipeline"""
        local_results = [
            {'title': 'Local Doc', 'content': 'Local content', 'score': 0.8}
        ]
        
        web_results = {
            'answer': 'Web answer',
            'results': [
                {'title': 'Web Result', 'content': 'Web content', 'score': 0.7, 'url': 'https://example.com'}
            ]
        }
        
        synthesized = await result_synthesizer.synthesize_results(local_results, web_results, "test query")
        
        assert 'query' in synthesized
        assert 'answer' in synthesized
        assert 'sources' in synthesized
        assert 'metadata' in synthesized
    
    @pytest.mark.asyncio
    async def test_result_merging(self):
        """Test result merging functionality"""
        local_results = [{'title': 'Local', 'content': 'content', 'score': 0.9}]
        web_results = {'results': [{'title': 'Web', 'url': 'https://test.com', 'score': 0.8}]}
        
        merged = await result_merger.merge_results(local_results, web_results, "test")
        
        assert 'sources' in merged
        assert 'source_breakdown' in merged
        assert merged['source_breakdown']['local'] >= 0
        assert merged['source_breakdown']['web'] >= 0