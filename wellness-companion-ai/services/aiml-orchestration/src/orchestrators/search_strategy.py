import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class SearchStrategy:
    """Determine optimal search strategy"""
    
    async def determine_strategy(
        self, 
        query: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Determine best search strategy: local_only, web_only, or hybrid"""
        
        # Check for explicit web indicators
        if self._requires_web_search(query):
            return "web_only"
        
        # Check for local-only indicators
        if self._is_local_query(query, context):
            return "local_only"
        
        # Default to hybrid for best coverage
        return "hybrid"
    
    def _requires_web_search(self, query: str) -> bool:
        """Check if query explicitly requires web search"""
        web_indicators = [
            "current", "latest", "recent", "news", "today", "2024", "2025",
            "trending", "breaking", "update", "price", "stock", "weather"
        ]
        
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in web_indicators)
    
    def _is_local_query(self, query: str, context: Optional[Dict[str, Any]]) -> bool:
        """Check if query should be handled locally only"""
        if not context or not context.get("has_documents"):
            return False
        
        local_indicators = [
            "my document", "uploaded file", "personal", "private",
            "according to my", "in my files", "from my notes"
        ]
        
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in local_indicators)

search_strategy = SearchStrategy()