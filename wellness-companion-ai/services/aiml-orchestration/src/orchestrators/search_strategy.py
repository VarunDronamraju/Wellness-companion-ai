
# File: services/aiml-orchestration/src/orchestrators/search_strategy.py
"""
Search Strategy - Decision logic for search approach
Location: services/aiml-orchestration/src/orchestrators/search_strategy.py
"""

import logging
import re
from typing import Dict, List, Optional, Any
from enum import Enum

logger = logging.getLogger(__name__)

class SearchType(Enum):
    VECTOR_ONLY = "vector_only"
    WEB_PREFERRED = "web_preferred"
    HYBRID = "hybrid"
    FACTUAL = "factual"

class SearchStrategy:
    """Determines optimal search strategy based on query characteristics"""
    
    def __init__(self):
        self.current_indicators = ['current', 'latest', 'recent', 'now', 'today', '2024', '2025']
        self.factual_indicators = ['what is', 'who is', 'when was', 'where is', 'how many']
        self.opinion_indicators = ['best', 'worst', 'top', 'review', 'compare']
        
    async def determine_strategy(self, query: str) -> Dict[str, Any]:
        """Determine search strategy based on query analysis"""
        query_lower = query.lower()
        
        # Check for current/recent information needs
        if any(indicator in query_lower for indicator in self.current_indicators):
            return {
                'type': SearchType.WEB_PREFERRED,
                'reason': 'current_information_required',
                'confidence_threshold': 0.3  # Lower threshold for web search
            }
        
        # Check for factual queries
        if any(indicator in query_lower for indicator in self.factual_indicators):
            return {
                'type': SearchType.FACTUAL,
                'reason': 'factual_query',
                'confidence_threshold': 0.8  # Higher threshold for factual
            }
        
        # Check for opinion-based queries
        if any(indicator in query_lower for indicator in self.opinion_indicators):
            return {
                'type': SearchType.HYBRID,
                'reason': 'opinion_comparison_needed',
                'confidence_threshold': 0.5  # Medium threshold
            }
        
        # Default hybrid approach
        return {
            'type': SearchType.HYBRID,
            'reason': 'general_query',
            'confidence_threshold': 0.7
        }
