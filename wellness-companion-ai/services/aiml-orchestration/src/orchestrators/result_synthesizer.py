import logging
from typing import Dict, List, Any, Optional
from .result_merger import ResultMerger
from .content_combiner import ContentCombiner
from .source_attribution import SourceAttribution
from .enhanced_response_builder import EnhancedResponseBuilder

logger = logging.getLogger(__name__)

class ResultSynthesizer:
    """Combine local + web results into enhanced responses"""
    
    def __init__(self):
        self.merger = ResultMerger()
        self.combiner = ContentCombiner()
        self.attribution = SourceAttribution()
        self.builder = EnhancedResponseBuilder()
    
    async def synthesize_results(
        self,
        local_results: List[Dict[str, Any]],
        web_results: Dict[str, Any],
        query: str,
        synthesis_type: str = "enhanced"
    ) -> Dict[str, Any]:
        """Main synthesis pipeline"""
        try:
            # Merge results from different sources
            merged_results = await self.merger.merge_results(local_results, web_results, query)
            
            # Combine content intelligently
            combined_content = await self.combiner.combine_content(merged_results, query)
            
            # Add source attribution
            attributed_content = await self.attribution.add_attribution(combined_content, merged_results)
            
            # Build enhanced response
            final_response = await self.builder.build_response(attributed_content, query, synthesis_type)
            
            logger.info(f"Synthesized response with {len(merged_results.get('sources', []))} sources")
            return final_response
            
        except Exception as e:
            logger.error(f"Result synthesis failed: {str(e)}")
            return await self.builder.build_fallback_response(query, str(e))

result_synthesizer = ResultSynthesizer()