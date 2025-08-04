
# File: services/aiml-orchestration/tests/test_confidence_scoring.py
"""
Test Confidence Scoring - Test confidence evaluation
Location: services/aiml-orchestration/tests/test_confidence_scoring.py
"""

import asyncio
from src.orchestrators.confidence_evaluator import ConfidenceEvaluator

class TestConfidenceScoring:
    """Test confidence scoring functionality"""
    
    def __init__(self):
        self.evaluator = ConfidenceEvaluator()
    
    async def test_high_confidence_results(self):
        """Test high confidence result evaluation"""
        high_quality_results = [
            {'content': 'Comprehensive ML guide with detailed explanations', 'score': 0.9},
            {'content': 'Advanced ML techniques and algorithms', 'score': 0.8},
            {'content': 'ML implementation best practices', 'score': 0.85}
        ]
        
        confidence = await self.evaluator.evaluate_confidence(high_quality_results, 'machine learning')
        assert confidence > 0.7, f"Expected high confidence, got {confidence}"
    
    async def test_low_confidence_results(self):
        """Test low confidence result evaluation"""
        low_quality_results = [
            {'content': 'ML', 'score': 0.3}
        ]
        
        confidence = await self.evaluator.evaluate_confidence(low_quality_results, 'machine learning')
        assert confidence < 0.7, f"Expected low confidence, got {confidence}"
    
    async def test_empty_results(self):
        """Test confidence evaluation with no results"""
        confidence = await self.evaluator.evaluate_confidence([], 'test query')
        assert confidence == 0.0
