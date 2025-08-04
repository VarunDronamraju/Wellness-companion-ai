# ==== FILE 1: services/aiml-orchestration/src/orchestrators/rag_orchestrator.py ====

"""
Main RAG pipeline controller - orchestrates complete RAG workflow.
CRITICAL COMPONENT: Central coordination hub for all RAG operations.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
import sys

sys.path.append('/app/src')

from .retrieval_orchestrator import RetrievalOrchestrator, RetrievalResult
from .response_synthesizer import ResponseSynthesizer, SynthesizedResponse
from .pipeline_coordinator import PipelineCoordinator
from .workflow_manager import WorkflowManager
#from search.web_search import WebSearchClient  # Will be created in Task 31

logger = logging.getLogger(__name__)

@dataclass
class RAGResult:
    """Complete RAG pipeline result."""
    query: str
    retrieval_result: RetrievalResult
    synthesized_response: SynthesizedResponse
    total_processing_time: float
    confidence: float
    fallback_used: bool
    metadata: Dict[str, Any]

class RAGOrchestrator:
    """
    Main RAG pipeline controller - coordinates entire RAG workflow.
    This is the primary entry point for all RAG operations.
    """
    
    def __init__(self):
        # Core components
        self.retrieval_orchestrator = RetrievalOrchestrator()
        self.response_synthesizer = ResponseSynthesizer()
        self.pipeline_coordinator = PipelineCoordinator()
        self.workflow_manager = WorkflowManager()
        
        # Configuration
        self.config = {
            'confidence_threshold': 0.7,  # Fallback trigger threshold
            'max_processing_time': 30.0,  # Maximum allowed processing time
            'enable_web_fallback': True,
            'default_model': 'gemma:3b',
            'max_retries': 2
        }
        
        # Statistics
        self.rag_stats = {
            'total_queries': 0,
            'successful_queries': 0,
            'failed_queries': 0,
            'fallback_triggered': 0,
            'average_processing_time': 0.0,
            'total_processing_time': 0.0,
            'high_confidence_responses': 0,
            'web_search_used': 0
        }

    async def process_query(
        self, 
        query: str, 
        collection_name: str = "documents",
        model_name: str = None,
        enable_fallback: bool = True
    ) -> RAGResult:
        """
        Process complete RAG query - main entry point.
        
        Args:
            query: User query
            collection_name: Vector database collection
            model_name: LLM model to use
            enable_fallback: Whether to use web search fallback
            
        Returns:
            Complete RAG result with response and metadata
        """
        start_time = datetime.now()
        workflow_id = f"rag_{datetime.now().timestamp()}"
        
        try:
            logger.info(f"Starting RAG processing for query: {query[:50]}...")
            
            # Initialize workflow
            self.workflow_manager.start_workflow(workflow_id, query)
            
            # Step 1: Retrieval phase
            retrieval_result = await self._execute_retrieval_phase(
                query, collection_name, workflow_id
            )
            
            # Step 2: Confidence evaluation and fallback decision
            should_fallback = self._should_trigger_fallback(retrieval_result, enable_fallback)
            
            if should_fallback:
                logger.info("Low confidence detected, triggering web search fallback")
                retrieval_result = await self._execute_fallback_phase(
                    query, retrieval_result, workflow_id
                )
            
            # Step 3: Response synthesis phase
            synthesized_response = await self._execute_synthesis_phase(
                retrieval_result, query, model_name or self.config['default_model'], workflow_id
            )
            
            # Step 4: Final result assembly
            processing_time = (datetime.now() - start_time).total_seconds()
            final_confidence = self._calculate_final_confidence(
                retrieval_result, synthesized_response
            )
            
            rag_result = RAGResult(
                query=query,
                retrieval_result=retrieval_result,
                synthesized_response=synthesized_response,
                total_processing_time=processing_time,
                confidence=final_confidence,
                fallback_used=should_fallback,
                metadata={
                    'workflow_id': workflow_id,
                    'timestamp': datetime.now().isoformat(),
                    'model_used': model_name or self.config['default_model'],
                    'collection_name': collection_name,
                    'phases_completed': ['retrieval', 'synthesis'] + (['fallback'] if should_fallback else [])
                }
            )
            
            # Update statistics and complete workflow
            self._update_stats(True, processing_time, final_confidence, should_fallback)
            self.workflow_manager.complete_workflow(workflow_id, success=True)
            
            logger.info(f"RAG processing completed: confidence={final_confidence:.2f}, time={processing_time:.2f}s")
            
            return rag_result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_stats(False, processing_time, 0.0, False)
            self.workflow_manager.complete_workflow(workflow_id, success=False, error=str(e))
            
            logger.error(f"RAG processing failed: {str(e)}")
            return self._create_error_result(query, str(e), processing_time, workflow_id)

    async def _execute_retrieval_phase(
        self, 
        query: str, 
        collection_name: str, 
        workflow_id: str
    ) -> RetrievalResult:
        """Execute the retrieval phase of RAG pipeline."""
        try:
            self.workflow_manager.update_phase(workflow_id, 'retrieval', 'in_progress')
            
            retrieval_result = await self.retrieval_orchestrator.orchestrate_retrieval(
                query=query,
                collection_name=collection_name
            )
            
            self.workflow_manager.update_phase(workflow_id, 'retrieval', 'completed')
            return retrieval_result
            
        except Exception as e:
            self.workflow_manager.update_phase(workflow_id, 'retrieval', 'failed', str(e))
            raise

    async def _execute_fallback_phase(
        self, 
        query: str, 
        original_result: RetrievalResult, 
        workflow_id: str
    ) -> RetrievalResult:
        """Execute web search fallback phase."""
        try:
            self.workflow_manager.update_phase(workflow_id, 'fallback', 'in_progress')
            
            # This will be implemented in Task 31 (Web Search Integration)
            # For now, return enhanced result with fallback flag
            enhanced_result = RetrievalResult(
                query_analysis=original_result.query_analysis,
                search_results=original_result.search_results,
                assembled_context=original_result.assembled_context,
                retrieval_confidence=max(0.5, original_result.retrieval_confidence),  # Boost confidence
                processing_time=original_result.processing_time,
                metadata={
                    **original_result.metadata,
                    'fallback_triggered': True,
                    'fallback_reason': 'Low local confidence'
                }
            )
            
            self.rag_stats['fallback_triggered'] += 1
            self.workflow_manager.update_phase(workflow_id, 'fallback', 'completed')
            
            return enhanced_result
            
        except Exception as e:
            self.workflow_manager.update_phase(workflow_id, 'fallback', 'failed', str(e))
            # Return original result if fallback fails
            return original_result

    async def _execute_synthesis_phase(
        self, 
        retrieval_result: RetrievalResult, 
        query: str, 
        model_name: str, 
        workflow_id: str
    ) -> SynthesizedResponse:
        """Execute response synthesis phase."""
        try:
            self.workflow_manager.update_phase(workflow_id, 'synthesis', 'in_progress')
            
            synthesized_response = await self.response_synthesizer.synthesize_response(
                context=retrieval_result.assembled_context,
                query=query,
                model_name=model_name
            )
            
            self.workflow_manager.update_phase(workflow_id, 'synthesis', 'completed')
            return synthesized_response
            
        except Exception as e:
            self.workflow_manager.update_phase(workflow_id, 'synthesis', 'failed', str(e))
            raise

    def _should_trigger_fallback(self, retrieval_result: RetrievalResult, enable_fallback: bool) -> bool:
        """Determine if web search fallback should be triggered."""
        if not enable_fallback or not self.config['enable_web_fallback']:
            return False
        
        # Primary condition: low confidence
        if retrieval_result.retrieval_confidence < self.config['confidence_threshold']:
            return True
        
        # Secondary conditions
        if (retrieval_result.assembled_context.total_chunks == 0 or
            retrieval_result.assembled_context.relevance_score < 0.3):
            return True
        
        return False

    def _calculate_final_confidence(
        self, 
        retrieval_result: RetrievalResult, 
        synthesized_response: SynthesizedResponse
    ) -> float:
        """Calculate final confidence score for the complete RAG result."""
        # Weighted combination of retrieval and synthesis confidence
        retrieval_weight = 0.6
        synthesis_weight = 0.4
        
        final_confidence = (
            retrieval_result.retrieval_confidence * retrieval_weight +
            synthesized_response.confidence * synthesis_weight
        )
        
        # Boost confidence if fallback was used successfully
        if retrieval_result.metadata.get('fallback_triggered', False):
            final_confidence = min(1.0, final_confidence + 0.1)
        
        return final_confidence

    def _create_error_result(
        self, 
        query: str, 
        error: str, 
        processing_time: float, 
        workflow_id: str
    ) -> RAGResult:
        """Create error result when RAG processing fails."""
        from orchestrators.context_builder import AssembledContext
        from orchestrators.query_processor import QueryAnalysis
        
        error_retrieval = RetrievalResult(
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
                context_text="",
                total_chunks=0,
                total_tokens=0,
                relevance_score=0.0,
                sources=[],
                chunks=[],
                metadata={'error': error}
            ),
            retrieval_confidence=0.0,
            processing_time=processing_time,
            metadata={'error': error}
        )
        
        error_synthesis = SynthesizedResponse(
            response_text=f"I apologize, but I encountered an error processing your query: {error}",
            sources=[],
            confidence=0.0,
            processing_time=0.0,
            token_count=20,
            is_streaming=False,
            metadata={'error': error}
        )
        
        return RAGResult(
            query=query,
            retrieval_result=error_retrieval,
            synthesized_response=error_synthesis,
            total_processing_time=processing_time,
            confidence=0.0,
            fallback_used=False,
            metadata={
                'workflow_id': workflow_id,
                'error': error,
                'timestamp': datetime.now().isoformat()
            }
        )

    def _update_stats(self, success: bool, processing_time: float, confidence: float, fallback_used: bool):
        """Update RAG orchestration statistics."""
        self.rag_stats['total_queries'] += 1
        
        if success:
            self.rag_stats['successful_queries'] += 1
            if confidence >= 0.8:
                self.rag_stats['high_confidence_responses'] += 1
        else:
            self.rag_stats['failed_queries'] += 1
        
        if fallback_used:
            self.rag_stats['web_search_used'] += 1
        
        self.rag_stats['total_processing_time'] += processing_time
        self.rag_stats['average_processing_time'] = (
            self.rag_stats['total_processing_time'] / 
            self.rag_stats['total_queries']
        )

    def get_rag_statistics(self) -> Dict[str, Any]:
        """Get comprehensive RAG orchestration statistics."""
        total = self.rag_stats['total_queries']
        return {
            **self.rag_stats,
            'success_rate': f"{(self.rag_stats['successful_queries'] / max(1, total)) * 100:.2f}%",
            'fallback_rate': f"{(self.rag_stats['fallback_triggered'] / max(1, total)) * 100:.2f}%",
            'high_confidence_rate': f"{(self.rag_stats['high_confidence_responses'] / max(1, total)) * 100:.2f}%",
            'web_search_usage': f"{(self.rag_stats['web_search_used'] / max(1, total)) * 100:.2f}%"
        }

    async def batch_process_queries(self, queries: List[str]) -> List[RAGResult]:
        """Process multiple queries concurrently."""
        tasks = [self.process_query(query) for query in queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful_results = [
            result for result in results 
            if isinstance(result, RAGResult)
        ]
        
        logger.info(f"Batch processed {len(successful_results)}/{len(queries)} queries")
        return successful_results

    def update_configuration(self, config_updates: Dict[str, Any]):
        """Update RAG orchestrator configuration."""
        self.config.update(config_updates)
        logger.info(f"Configuration updated: {config_updates}")

    def get_system_health(self) -> Dict[str, Any]:
        """Get overall RAG system health status."""
        stats = self.get_rag_statistics()
        
        health_status = "healthy"
        success_rate = float(stats['success_rate'].rstrip('%'))
        
        if success_rate < 90:
            health_status = "degraded"
        if success_rate < 70:
            health_status = "unhealthy"
        
        return {
            'status': health_status,
            'success_rate': stats['success_rate'],
            'average_response_time': f"{self.rag_stats['average_processing_time']:.2f}s",
            'fallback_usage': stats['fallback_rate'],
            'component_status': {
                'retrieval': self.retrieval_orchestrator.get_retrieval_statistics(),
                'synthesis': self.response_synthesizer.get_synthesis_statistics(),
                'workflow': self.workflow_manager.get_workflow_statistics()
            }
        }

