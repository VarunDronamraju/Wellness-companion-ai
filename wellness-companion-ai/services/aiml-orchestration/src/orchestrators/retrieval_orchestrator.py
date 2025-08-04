"""
Retrieval orchestration for RAG pipeline.
Coordinates search operations and result processing.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import sys
import os

# Add src to path for imports
sys.path.append('/app/src')

from .query_processor import QueryProcessor, QueryAnalysis
from .context_builder import ContextBuilder, AssembledContext
from search.vector_search import VectorSearch

logger = logging.getLogger(__name__)

@dataclass
class RetrievalResult:
    """Complete retrieval result with context and metadata."""
    query_analysis: QueryAnalysis
    search_results: List[Dict[str, Any]]
    assembled_context: AssembledContext
    retrieval_confidence: float
    processing_time: float
    metadata: Dict[str, Any]

class RetrievalOrchestrator:
    """
    Orchestrates the complete retrieval process for RAG pipeline.
    Coordinates query processing, vector search, and context assembly.
    """
    
    def __init__(self):
        self.query_processor = QueryProcessor()
        self.context_builder = ContextBuilder()
        self.vector_search = VectorSearch()
        
        self.retrieval_stats = {
            'total_retrievals': 0,
            'successful_retrievals': 0,
            'failed_retrievals': 0,
            'average_retrieval_time': 0.0,
            'total_retrieval_time': 0.0,
            'high_confidence_retrievals': 0,
            'low_confidence_retrievals': 0,
            'fallback_triggered': 0
        }
        
        # Thresholds for confidence-based decisions
        self.confidence_thresholds = {
            'high_confidence': 0.8,
            'medium_confidence': 0.6,
            'low_confidence': 0.4,
            'fallback_threshold': 0.7  # Below this triggers web search fallback
        }

    async def orchestrate_retrieval(
        self, 
        query: str, 
        collection_name: str = "documents",
        context_type: str = "comprehensive",
        max_results: int = 10
    ) -> RetrievalResult:
        """
        Orchestrate complete retrieval process.
        
        Args:
            query: User query
            collection_name: Vector database collection
            context_type: Type of context to build
            max_results: Maximum search results to retrieve
            
        Returns:
            Complete retrieval result with context
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"Starting retrieval orchestration for query: {query[:50]}...")
            
            # Step 1: Process and analyze query
            query_analysis = await self.query_processor.process_query(query)
            logger.debug(f"Query processed: intent={query_analysis.intent}, confidence={query_analysis.confidence}")
            
            # Step 2: Perform vector search with processed query
            search_results = await self._perform_vector_search(
                query=query_analysis.processed_query,
                original_query=query,
                collection_name=collection_name,
                limit=max_results,
                query_analysis=query_analysis
            )
            
            # Step 3: Build context from search results
            assembled_context = await self.context_builder.build_context(
                search_results=search_results,
                query=query,
                context_type=context_type
            )
            
            # Step 4: Calculate overall retrieval confidence
            retrieval_confidence = self._calculate_retrieval_confidence(
                query_analysis, search_results, assembled_context
            )
            
            # Step 5: Prepare final result
            processing_time = (datetime.now() - start_time).total_seconds()
            
            retrieval_result = RetrievalResult(
                query_analysis=query_analysis,
                search_results=search_results,
                assembled_context=assembled_context,
                retrieval_confidence=retrieval_confidence,
                processing_time=processing_time,
                metadata={
                    'timestamp': datetime.now().isoformat(),
                    'collection_name': collection_name,
                    'context_type': context_type,
                    'search_result_count': len(search_results),
                    'fallback_recommended': retrieval_confidence < self.confidence_thresholds['fallback_threshold'],
                    'confidence_level': self._get_confidence_level(retrieval_confidence)
                }
            )
            
            self._update_stats(True, processing_time, retrieval_confidence)
            logger.info(f"Retrieval completed: confidence={retrieval_confidence:.2f}, context_chunks={assembled_context.total_chunks}")
            
            return retrieval_result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_stats(False, processing_time, 0.0)
            logger.error(f"Error in retrieval orchestration: {str(e)}")
            
            return self._create_error_result(query, str(e), processing_time)

    async def _perform_vector_search(
        self,
        query: str,
        original_query: str,
        collection_name: str,
        limit: int,
        query_analysis: QueryAnalysis
    ) -> List[Dict[str, Any]]:
        """Perform vector search with enhanced query."""
        try:
            # Try search with processed query first
            search_result = await asyncio.to_thread(
                self.vector_search.search_with_text,
                query_text=query,
                collection_name=collection_name,
                limit=limit
            )
            
            if search_result['success'] and search_result['results']:
                logger.debug(f"Vector search successful: {len(search_result['results'])} results")
                return search_result['results']
            
            # Fallback to original query if processed query fails
            if query != original_query:
                logger.debug("Trying fallback search with original query")
                fallback_result = await asyncio.to_thread(
                    self.vector_search.search_with_text,
                    query_text=original_query,
                    collection_name=collection_name,
                    limit=limit
                )
                
                if fallback_result['success'] and fallback_result['results']:
                    return fallback_result['results']
            
            logger.warning(f"Vector search returned no results for query: {query}")
            return []
            
        except Exception as e:
            logger.error(f"Error in vector search: {str(e)}")
            return []

    def _calculate_retrieval_confidence(
        self,
        query_analysis: QueryAnalysis,
        search_results: List[Dict[str, Any]],
        assembled_context: AssembledContext
    ) -> float:
        """Calculate overall retrieval confidence score."""
        confidence_factors = {}
        
        # Query processing confidence (20%)
        confidence_factors['query_confidence'] = query_analysis.confidence * 0.2
        
        # Search results quality (40%)
        if search_results:
            avg_score = sum(result.get('score', 0) for result in search_results) / len(search_results)
            result_count_factor = min(1.0, len(search_results) / 5)  # Optimal around 5 results
            confidence_factors['search_confidence'] = (avg_score * 0.7 + result_count_factor * 0.3) * 0.4
        else:
            confidence_factors['search_confidence'] = 0.0
        
        # Context assembly quality (30%)
        context_quality = assembled_context.relevance_score
        chunk_diversity = min(1.0, len(assembled_context.sources) / 3)  # Diversity bonus
        confidence_factors['context_confidence'] = (context_quality * 0.8 + chunk_diversity * 0.2) * 0.3
        
        # Token efficiency (10%)
        if assembled_context.total_tokens > 0:
            token_efficiency = min(1.0, assembled_context.total_tokens / 2000)  # Optimal token usage
            confidence_factors['token_efficiency'] = token_efficiency * 0.1
        else:
            confidence_factors['token_efficiency'] = 0.0
        
        total_confidence = sum(confidence_factors.values())
        
        logger.debug(f"Confidence factors: {confidence_factors}, total: {total_confidence:.2f}")
        
        return min(1.0, total_confidence)

    def _get_confidence_level(self, confidence: float) -> str:
        """Get human-readable confidence level."""
        if confidence >= self.confidence_thresholds['high_confidence']:
            return 'high'
        elif confidence >= self.confidence_thresholds['medium_confidence']:
            return 'medium'
        elif confidence >= self.confidence_thresholds['low_confidence']:
            return 'low'
        else:
            return 'very_low'

    def _create_error_result(self, query: str, error: str, processing_time: float) -> RetrievalResult:
        """Create error result when retrieval fails."""
        return RetrievalResult(
            query_analysis=QueryAnalysis(
                original_query=query,
                processed_query=query,
                intent='unknown',
                entities=[],
                keywords=[],
                query_type='unknown',
                confidence=0.0,
                metadata={'error': error}
            ),
            search_results=[],
            assembled_context=AssembledContext(
                context_text=f"Retrieval failed: {error}",
                total_chunks=0,
                total_tokens=10,
                relevance_score=0.0,
                sources=[],
                chunks=[],
                metadata={'error': error}
            ),
            retrieval_confidence=0.0,
            processing_time=processing_time,
            metadata={
                'timestamp': datetime.now().isoformat(),
                'error': error,
                'fallback_recommended': True
            }
        )

    def _update_stats(self, success: bool, processing_time: float, confidence: float):
        """Update retrieval statistics."""
        self.retrieval_stats['total_retrievals'] += 1
        
        if success:
            self.retrieval_stats['successful_retrievals'] += 1
            
            # Confidence level tracking
            if confidence >= self.confidence_thresholds['high_confidence']:
                self.retrieval_stats['high_confidence_retrievals'] += 1
            elif confidence < self.confidence_thresholds['fallback_threshold']:
                self.retrieval_stats['low_confidence_retrievals'] += 1
                self.retrieval_stats['fallback_triggered'] += 1
        else:
            self.retrieval_stats['failed_retrievals'] += 1
        
        self.retrieval_stats['total_retrieval_time'] += processing_time
        self.retrieval_stats['average_retrieval_time'] = (
            self.retrieval_stats['total_retrieval_time'] / 
            self.retrieval_stats['total_retrievals']
        )

    def get_retrieval_statistics(self) -> Dict[str, Any]:
        """Get comprehensive retrieval statistics."""
        total = self.retrieval_stats['total_retrievals']
        return {
            **self.retrieval_stats,
            'success_rate': f"{(self.retrieval_stats['successful_retrievals'] / max(1, total)) * 100:.2f}%",
            'fallback_rate': f"{(self.retrieval_stats['fallback_triggered'] / max(1, total)) * 100:.2f}%",
            'high_confidence_rate': f"{(self.retrieval_stats['high_confidence_retrievals'] / max(1, total)) * 100:.2f}%"
        }

    async def batch_retrieve(
        self, 
        queries: List[str], 
        collection_name: str = "documents"
    ) -> List[RetrievalResult]:
        """Process multiple queries concurrently."""
        tasks = [
            self.orchestrate_retrieval(query, collection_name) 
            for query in queries
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful results
        successful_results = [
            result for result in results 
            if isinstance(result, RetrievalResult)
        ]
        
        logger.info(f"Batch retrieval completed: {len(successful_results)}/{len(queries)} successful")
        return successful_results

    def should_trigger_web_fallback(self, retrieval_result: RetrievalResult) -> bool:
        """Determine if web search fallback should be triggered."""
        return (
            retrieval_result.retrieval_confidence < self.confidence_thresholds['fallback_threshold'] or
            retrieval_result.assembled_context.total_chunks == 0 or
            retrieval_result.assembled_context.relevance_score < 0.3
        )

    async def adaptive_retrieve(
        self, 
        query: str, 
        collection_name: str = "documents"
    ) -> RetrievalResult:
        """
        Adaptive retrieval that adjusts parameters based on query characteristics.
        """
        # Analyze query to determine optimal parameters
        query_analysis = await self.query_processor.process_query(query)
        
        # Adjust parameters based on query type
        if query_analysis.query_type == 'complex':
            context_type = 'comprehensive'
            max_results = 15
        elif query_analysis.query_type == 'factual':
            context_type = 'focused'
            max_results = 5
        else:
            context_type = 'comprehensive'
            max_results = 10
        
        return await self.orchestrate_retrieval(
            query=query,
            collection_name=collection_name,
            context_type=context_type,
            max_results=max_results
        )

    def get_performance_insights(self) -> Dict[str, Any]:
        """Get performance insights and recommendations."""
        stats = self.get_retrieval_statistics()
        
        insights = {
            'performance_grade': 'A',
            'bottlenecks': [],
            'recommendations': [],
            'health_status': 'healthy'
        }
        
        # Analyze performance
        if float(stats['success_rate'].rstrip('%')) < 90:
            insights['bottlenecks'].append('Low success rate')
            insights['recommendations'].append('Review vector search parameters')
            insights['performance_grade'] = 'B'
        
        if self.retrieval_stats['average_retrieval_time'] > 2.0:
            insights['bottlenecks'].append('High response time')
            insights['recommendations'].append('Optimize vector search or reduce context size')
            insights['performance_grade'] = 'C'
        
        if float(stats['fallback_rate'].rstrip('%')) > 30:
            insights['bottlenecks'].append('High fallback rate')
            insights['recommendations'].append('Improve document indexing or query processing')
        
        return insights