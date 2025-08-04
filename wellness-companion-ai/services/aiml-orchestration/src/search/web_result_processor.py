import logging
from typing import Dict, List, Any, Optional
from .result_parser import ResultParser
from .content_extractor import ContentExtractor
from .result_validator import ResultValidator
from .metadata_enricher import MetadataEnricher

logger = logging.getLogger(__name__)

class WebResultProcessor:
    """Main processor for Tavily web search results"""
    
    def __init__(self):
        self.parser = ResultParser()
        self.extractor = ContentExtractor()
        self.validator = ResultValidator()
        self.enricher = MetadataEnricher()
    
    async def process_results(self, tavily_response: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Process complete Tavily response"""
        try:
            # Parse raw response
            parsed_results = self.parser.parse_tavily_response(tavily_response)
            
            # Extract and clean content
            for result in parsed_results.get('results', []):
                result['content'] = self.extractor.extract_clean_content(result.get('content', ''))
                result['title'] = self.extractor.clean_title(result.get('title', ''))
            
            # Validate results
            valid_results = self.validator.filter_valid_results(parsed_results.get('results', []))
            parsed_results['results'] = valid_results
            
            # Enrich with metadata
            enriched_results = await self.enricher.enrich_results(parsed_results, query)
            
            logger.info(f"Processed {len(valid_results)} valid results from {len(tavily_response.get('results', []))} raw results")
            return enriched_results
            
        except Exception as e:
            logger.error(f"Error processing web results: {str(e)}")
            return {'results': [], 'error': str(e)}

web_result_processor = WebResultProcessor()