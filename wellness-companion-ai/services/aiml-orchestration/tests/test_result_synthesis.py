
# File: services/aiml-orchestration/tests/test_result_synthesis.py
"""
Test Result Synthesis - Test result combination
Location: services/aiml-orchestration/tests/test_result_synthesis.py
"""

import asyncio
from src.orchestrators.result_synthesizer import ResultSynthesizer
from src.orchestrators.result_merger import ResultMerger

class TestResultSynthesis:
    """Test result synthesis functionality"""
    
    def __init__(self):
        self.synthesizer = ResultSynthesizer()
        self.merger = ResultMerger()
    
    async def test_result_merging(self):
        """Test merging of local and web results"""
        local_results = [{'content': 'Local info', 'title': 'Local', 'score': 0.8}]
        web_results = [{'content': 'Web info', 'title': 'Web', 'score': 0.7}]
        
        merged = await self.merger.merge_results(local_results, web_results)
        
        assert len(merged) == 2
        assert any(r.get('result_source') == 'local' for r in merged)
        assert any(r.get('result_source') == 'web' for r in merged)
    
    async def test_content_synthesis(self):
        """Test content synthesis"""
        local_results = [{'content': 'ML is AI subset', 'title': 'ML Guide', 'score': 0.8}]
        web_results = [{'content': 'ML trends 2025', 'title': 'Trends', 'score': 0.7}]
        
        result = await self.synthesizer.synthesize_results(local_results, web_results, 'machine learning')
        
        assert 'content' in result
        assert len(result['content']) > 0
