"""
Web Result Processor - Main orchestrator for processing Tavily API responses
Location: services/aiml-orchestration/src/search/web_result_processor.py

This module coordinates the entire web search result processing pipeline:
1. Parse raw Tavily responses
2. Extract relevant content
3. Validate and filter results
4. Enrich with metadata and source attribution
5. Format for RAG integration
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from .result_parser import ResultParser
from .content_extractor import ContentExtractor
from .result_validator import ResultValidator
from .metadata_enricher import MetadataEnricher

logger = logging.getLogger(__name__)

@dataclass
class ProcessedWebResult:
    """Structured web search result ready for RAG integration"""
    content: str
    title: str
    url: str
    snippet: str
    relevance_score: float
    confidence_score: float
    source_type: str
    timestamp: datetime
    citations: Dict[str, Any]
    metadata: Dict[str, Any]
    chunks: List[str]

class WebResultProcessor:
    """
    Main orchestrator for processing web search results from Tavily API
    
    This class coordinates the entire processing pipeline to transform
    raw Tavily responses into structured, validated results ready for
    RAG integration with local vector search results.
    """
    
    def __init__(self):
        """Initialize all processing components"""
        self.parser = ResultParser()
        self.content_extractor = ContentExtractor()
        self.validator = ResultValidator()
        self.metadata_enricher = MetadataEnricher()
        
        # Processing configuration
        self.max_results = 10
        self.min_content_length = 100
        self.max_content_length = 5000
        
        logger.info("WebResultProcessor initialized with all components")
    
    async def process_web_results(
        self, 
        tavily_response: Dict[str, Any],
        query: str,
        max_results: Optional[int] = None
    ) -> List[ProcessedWebResult]:
        """
        Main processing pipeline for Tavily web search results
        
        Args:
            tavily_response: Raw response from Tavily API
            query: Original search query for context
            max_results: Maximum number of results to process
            
        Returns:
            List of ProcessedWebResult objects ready for RAG integration
        """
        try:
            max_results = max_results or self.max_results
            logger.info(f"Processing web results for query: '{query}' (max: {max_results})")
            
            # Step 1: Parse raw Tavily response
            raw_results = await self.parser.parse_tavily_response(tavily_response)
            if not raw_results:
                logger.warning("No results found in Tavily response")
                return []
            
            logger.info(f"Parsed {len(raw_results)} raw results from Tavily")
            
            # Step 2: Extract and clean content
            extracted_results = []
            for result in raw_results[:max_results]:
                try:
                    extracted = await self.content_extractor.extract_relevant_content(
                        result, query
                    )
                    if extracted:
                        extracted_results.append(extracted)
                except Exception as e:
                    logger.warning(f"Failed to extract content from result: {e}")
                    continue
            
            logger.info(f"Extracted content from {len(extracted_results)} results")
            
            # Step 3: Validate and filter results
            validated_results = await self.validator.validate_results(
                extracted_results, query
            )
            
            logger.info(f"Validated {len(validated_results)} results")
            
            # Step 4: Enrich with metadata and source attribution
            enriched_results = []
            for result in validated_results:
                try:
                    enriched = await self.metadata_enricher.enrich_with_metadata(
                        result, query
                    )
                    enriched_results.append(enriched)
                except Exception as e:
                    logger.warning(f"Failed to enrich result metadata: {e}")
                    continue
            
            # Step 5: Convert to ProcessedWebResult objects
            processed_results = []
            for result in enriched_results:
                try:
                    processed = self._convert_to_processed_result(result)
                    processed_results.append(processed)
                except Exception as e:
                    logger.warning(f"Failed to convert result: {e}")
                    continue
            
            logger.info(f"Successfully processed {len(processed_results)} web results")
            return processed_results
            
        except Exception as e:
            logger.error(f"Error in web result processing pipeline: {e}")
            return []
    
    def _convert_to_processed_result(self, enriched_result: Dict[str, Any]) -> ProcessedWebResult:
        """Convert enriched result dictionary to ProcessedWebResult object"""
        return ProcessedWebResult(
            content=enriched_result.get('content', ''),
            title=enriched_result.get('title', ''),
            url=enriched_result.get('url', ''),
            snippet=enriched_result.get('snippet', ''),
            relevance_score=enriched_result.get('relevance_score', 0.0),
            confidence_score=enriched_result.get('confidence_score', 0.0),
            source_type=enriched_result.get('source_type', 'web'),
            timestamp=enriched_result.get('timestamp', datetime.utcnow()),
            citations=enriched_result.get('citations', {}),
            metadata=enriched_result.get('metadata', {}),
            chunks=enriched_result.get('chunks', [])
        )
    
    async def format_for_rag(
        self, 
        processed_results: List[ProcessedWebResult],
        query: str
    ) -> Dict[str, Any]:
        """
        Format processed results for RAG integration
        
        Args:
            processed_results: List of processed web results
            query: Original search query
            
        Returns:
            Dictionary formatted for RAG system integration
        """
        try:
            if not processed_results:
                return {
                    'results': [],
                    'total_results': 0,
                    'avg_confidence': 0.0,
                    'sources': [],
                    'query': query,
                    'processed_at': datetime.utcnow().isoformat()
                }
            
            # Calculate aggregate metrics
            total_results = len(processed_results)
            avg_confidence = sum(r.confidence_score for r in processed_results) / total_results
            avg_relevance = sum(r.relevance_score for r in processed_results) / total_results
            
            # Extract unique sources
            sources = list(set(r.url for r in processed_results))
            
            # Format results for RAG
            formatted_results = []
            for result in processed_results:
                formatted_results.append({
                    'content': result.content,
                    'title': result.title,
                    'url': result.url,
                    'snippet': result.snippet,
                    'relevance_score': result.relevance_score,
                    'confidence_score': result.confidence_score,
                    'source_type': result.source_type,
                    'timestamp': result.timestamp.isoformat(),
                    'citations': result.citations,
                    'metadata': result.metadata,
                    'chunks': result.chunks
                })
            
            rag_formatted = {
                'results': formatted_results,
                'total_results': total_results,
                'avg_confidence': avg_confidence,
                'avg_relevance': avg_relevance,
                'sources': sources,
                'query': query,
                'processed_at': datetime.utcnow().isoformat(),
                'processing_stats': {
                    'max_confidence': max((r.confidence_score for r in processed_results), default=0.0),
                    'min_confidence': min((r.confidence_score for r in processed_results), default=0.0),
                    'max_relevance': max((r.relevance_score for r in processed_results), default=0.0),
                    'min_relevance': min((r.relevance_score for r in processed_results), default=0.0),
                    'total_chunks': sum(len(r.chunks) for r in processed_results),
                    'avg_content_length': sum(len(r.content) for r in processed_results) / total_results
                }
            }
            
            logger.info(f"Formatted {total_results} results for RAG integration")
            return rag_formatted
            
        except Exception as e:
            logger.error(f"Error formatting results for RAG: {e}")
            return {
                'results': [],
                'total_results': 0,
                'avg_confidence': 0.0,
                'sources': [],
                'query': query,
                'error': str(e),
                'processed_at': datetime.utcnow().isoformat()
            }
    
    async def get_processing_stats(
        self, 
        processed_results: List[ProcessedWebResult]
    ) -> Dict[str, Any]:
        """Get detailed processing statistics"""
        if not processed_results:
            return {'total_results': 0}
        
        return {
            'total_results': len(processed_results),
            'avg_confidence': sum(r.confidence_score for r in processed_results) / len(processed_results),
            'avg_relevance': sum(r.relevance_score for r in processed_results) / len(processed_results),
            'avg_content_length': sum(len(r.content) for r in processed_results) / len(processed_results),
            'total_chunks': sum(len(r.chunks) for r in processed_results),
            'unique_sources': len(set(r.url for r in processed_results)),
            'source_types': list(set(r.source_type for r in processed_results))
        }