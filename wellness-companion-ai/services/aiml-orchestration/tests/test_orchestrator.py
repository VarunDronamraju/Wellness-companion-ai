# ==== FILE 5: services/aiml-orchestration/tests/test_orchestrator.py ====

"""
Orchestrator component tests.
Tests for individual orchestrator components.
"""

import unittest
import asyncio
import sys

sys.path.append('/app/src')

from orchestrators.query_processor import QueryProcessor, QueryAnalysis
from orchestrators.context_builder import ContextBuilder, AssembledContext
from orchestrators.response_synthesizer import ResponseSynthesizer
from orchestrators.workflow_manager import WorkflowManager
from reranking.confidence_scorer import ConfidenceScorer

class TestOrchestrators(unittest.TestCase):
    """Test orchestrator components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.query_processor = QueryProcessor()
        self.context_builder = ContextBuilder()
        self.response_synthesizer = ResponseSynthesizer()
        self.workflow_manager = WorkflowManager()
        self.confidence_scorer = ConfidenceScorer()

    def test_query_processor(self):
        """Test query processing functionality."""
        async def run_test():
            query = "What is machine learning?"
            analysis = await self.query_processor.process_query(query)
            
            # Verify analysis structure
            self.assertIsInstance(analysis, QueryAnalysis)
            self.assertEqual(analysis.original_query, query)
            self.assertIsNotNone(analysis.processed_query)
            self.assertIsNotNone(analysis.intent)
            self.assertIsNotNone(analysis.keywords)
            self.assertGreaterEqual(analysis.confidence, 0.0)
            self.assertLessEqual(analysis.confidence, 1.0)
            
            return analysis
        
        analysis = asyncio.run(run_test())
        self.assertIsNotNone(analysis)

    def test_query_processor_batch(self):
        """Test batch query processing."""
        async def run_test():
            queries = [
                "What is AI?",
                "How does machine learning work?", 
                "Explain neural networks"
            ]
            
            analyses = await self.query_processor.batch_process_queries(queries)
            
            # Verify batch results
            self.assertIsInstance(analyses, list)
            self.assertEqual(len(analyses), len(queries))
            
            for analysis in analyses:
                self.assertIsInstance(analysis, QueryAnalysis)
                self.assertIn(analysis.original_query, queries)
            
            return analyses
        
        analyses = asyncio.run(run_test())
        self.assertGreater(len(analyses), 0)

    def test_context_builder(self):
        """Test context building functionality."""
        async def run_test():
            # Mock search results
            search_results = [
                {
                    'content': 'Machine learning is a subset of AI.',
                    'score': 0.9,
                    'source': 'AI Textbook',
                    'id': 'doc1'
                },
                {
                    'content': 'Deep learning uses neural networks.',
                    'score': 0.8,
                    'source': 'ML Guide',
                    'id': 'doc2'
                }
            ]
            
            query = "What is machine learning?"
            context = await self.context_builder.build_context(search_results, query)
            
            # Verify context structure
            self.assertIsInstance(context, AssembledContext)
            self.assertIsNotNone(context.context_text)
            self.assertEqual(context.total_chunks, len(search_results))
            self.assertGreater(context.total_tokens, 0)
            self.assertGreaterEqual(context.relevance_score, 0.0)
            self.assertLessEqual(context.relevance_score, 1.0)
            self.assertEqual(len(context.sources), 2)
            
            return context
        
        context = asyncio.run(run_test())
        self.assertIsNotNone(context)

    def test_context_builder_empty_results(self):
        """Test context builder with empty results."""
        async def run_test():
            context = await self.context_builder.build_context([], "test query")
            
            # Should handle empty results gracefully
            self.assertIsInstance(context, AssembledContext)
            self.assertEqual(context.total_chunks, 0)
            self.assertEqual(len(context.sources), 0)
            
            return context
        
        context = asyncio.run(run_test())
        self.assertIsNotNone(context)

    def test_workflow_manager(self):
        """Test workflow management."""
        workflow_id = "test_workflow_123"
        query = "Test workflow query"
        
        # Start workflow
        workflow = self.workflow_manager.start_workflow(workflow_id, query)
        self.assertIsNotNone(workflow)
        self.assertEqual(workflow.workflow_id, workflow_id)
        self.assertEqual(workflow.query, query)
        
        # Update phase
        success = self.workflow_manager.update_phase(workflow_id, "retrieval", "in_progress")
        self.assertTrue(success)
        
        # Complete phase
        success = self.workflow_manager.update_phase(workflow_id, "retrieval", "completed")
        self.assertTrue(success)
        
        # Get workflow status
        status = self.workflow_manager.get_workflow_status(workflow_id)
        self.assertIsNotNone(status)
        self.assertEqual(status['workflow_id'], workflow_id)
        
        # Complete workflow
        success = self.workflow_manager.complete_workflow(workflow_id, success=True)
        self.assertTrue(success)

    def test_confidence_scorer(self):
        """Test confidence scoring."""
        # Test with no input (should return low confidence)
        confidence = self.confidence_scorer.calculate_confidence()
        
        self.assertIsNotNone(confidence)
        self.assertGreaterEqual(confidence.overall_confidence, 0.0)
        self.assertLessEqual(confidence.overall_confidence, 1.0)
        self.assertIsNotNone(confidence.confidence_level)
        self.assertIsInstance(confidence.fallback_recommended, bool)
        self.assertIsNotNone(confidence.component_scores)

    def test_component_statistics(self):
        """Test that all components track statistics properly."""
        # Query processor stats
        query_stats = self.query_processor.get_processing_statistics()
        self.assertIsInstance(query_stats, dict)
        self.assertIn('total_processed', query_stats)
        
        # Context builder stats
        context_stats = self.context_builder.get_build_statistics()
        self.assertIsInstance(context_stats, dict)
        self.assertIn('total_contexts_built', context_stats)
        
        # Response synthesizer stats
        synthesis_stats = self.response_synthesizer.get_synthesis_statistics()
        self.assertIsInstance(synthesis_stats, dict)
        self.assertIn('total_syntheses', synthesis_stats)
        
        # Workflow manager stats
        workflow_stats = self.workflow_manager.get_workflow_statistics()
        self.assertIsInstance(workflow_stats, dict)
        self.assertIn('total_workflows', workflow_stats)
        
        # Confidence scorer stats
        confidence_stats = self.confidence_scorer.get_scoring_statistics()
        self.assertIsInstance(confidence_stats, dict)
        self.assertIn('total_scores_calculated', confidence_stats)
