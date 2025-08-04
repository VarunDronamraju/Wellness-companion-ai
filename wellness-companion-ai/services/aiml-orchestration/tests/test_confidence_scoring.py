import pytest
import asyncio
from src.orchestrators.confidence_evaluator import confidence_evaluator

class TestConfidenceScoring:
    
    @pytest.mark.asyncio
    async def test_high_confidence_scenario(self):
        """Test high confidence results"""
        high_quality_results = [
            {'score': 0.9, 'content': 'highly relevant content matching query terms', 'title': 'Perfect Match'},
            {'score': 0.85, 'content': 'also relevant content', 'title': 'Good Match'}
        ]
        
        confidence = await confidence_evaluator.evaluate_local_confidence(high_quality_results, "relevant query")
        assert confidence > 0.7
        assert not confidence_evaluator.should_trigger_fallback(confidence)
    
    @pytest.mark.asyncio
    async def test_low_confidence_scenario(self):
        """Test low confidence triggers fallback"""
        low_quality_results = [
            {'score': 0.3, 'content': 'barely relevant', 'title': 'Weak Match'}
        ]
        
        confidence = await confidence_evaluator.evaluate_local_confidence(low_quality_results, "specific query")
        should_fallback = confidence_evaluator.should_trigger_fallback(confidence)
        
        assert confidence < 0.7
        assert should_fallback == True
    
    @pytest.mark.asyncio
    async def test_empty_results_confidence(self):
        """Test confidence with no results"""
        confidence = await confidence_evaluator.evaluate_local_confidence([], "any query")
        assert confidence == 0.0
        assert confidence_evaluator.should_trigger_fallback(confidence)