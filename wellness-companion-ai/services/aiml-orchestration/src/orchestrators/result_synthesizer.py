# File: services/aiml-orchestration/src/orchestrators/result_synthesizer.py
"""
Result Synthesizer - Combine local + web results into enhanced responses
Location: services/aiml-orchestration/src/orchestrators/result_synthesizer.py
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .result_merger import ResultMerger
from .content_combiner import ContentCombiner
from .source_attribution import SourceAttribution
from .enhanced_response_builder import EnhancedResponseBuilder

logger = logging.getLogger(__name__)

class ResultSynthesizer:
    """Combines local + web results into enhanced responses"""
    
    def __init__(self):
        self.result_merger = ResultMerger()
        self.content_combiner = ContentCombiner()
        self.source_attribution = SourceAttribution()
        self.response_builder = EnhancedResponseBuilder()
        
    async def synthesize_results(
        self, 
        local_results: List[Dict[str, Any]], 
        web_results: List[Dict[str, Any]], 
        query: str
    ) -> Dict[str, Any]:
        """Synthesize local and web results into enhanced response"""
        try:
            # Merge results with deduplication
            merged_results = await self.result_merger.merge_results(local_results, web_results)
            
            # Combine content coherently
            combined_content = await self.content_combiner.combine_content(merged_results, query)
            
            # Add source attribution
            attributed_content = await self.source_attribution.add_attribution(
                combined_content, merged_results
            )
            
            # Build enhanced response
            enhanced_response = await self.response_builder.build_response(
                attributed_content, merged_results, query
            )
            
            return enhanced_response
            
        except Exception as e:
            logger.error(f"Result synthesis error: {e}")
            return {'content': '', 'sources': [], 'error': str(e)}
