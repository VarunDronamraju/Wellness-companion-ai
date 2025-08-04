# File: services/aiml-orchestration/tests/test_hybrid_search.py
"""
Test Hybrid Search - Test hybrid search functionality
Location: services/aiml-orchestration/tests/test_hybrid_search.py
"""

import asyncio
import pytest
from typing import Dict, List, Any

from src.orchestrators.hybrid_search import HybridSearch
from src.orchestrators.search_strategy import SearchStrategy, SearchType
from src.orchestrators.confidence_evaluator import ConfidenceEvaluator

class TestHybridSearch:
    """Test suite for hybrid search functionality"""
    
    def __init__(self):
        self.mock_vector_results = [
            {'content': 'Machine learning basics', 'title': 'ML Guide', 'score': 0.8},
            {'content': 'Deep learning overview', 'title': 'DL Tutorial', 'score': 0.6}
        ]
        
        self.mock_web_results = [
            {'content': 'Latest ML trends 2025', 'title': 'ML Trends', 'score': 0.9},
            {'content': 'AI developments', 'title': 'AI News', 'score': 0.7}
        ]
    
    async def test_confidence_threshold_trigger(self):
        """Test that low confidence triggers web fallback"""
        evaluator = ConfidenceEvaluator()
        
        # Low confidence results
        low_conf_results = [{'content': 'short', 'score': 0.3}]
        confidence = await evaluator.evaluate_confidence(low_conf_results, 'test query')
        
        assert confidence < 0.7, f"Expected low confidence, got {confidence}"
    
    async def test_search_strategy_determination(self):
        """Test search strategy determination"""
        strategy = SearchStrategy()
        
        # Current information query
        current_strategy = await strategy.determine_strategy('latest AI trends 2025')
        assert current_strategy['type'] == SearchType.WEB_PREFERRED
        
        # Factual query
        factual_strategy = await strategy.determine_strategy('what is machine learning')
        assert factual_strategy['type'] == SearchType.FACTUAL