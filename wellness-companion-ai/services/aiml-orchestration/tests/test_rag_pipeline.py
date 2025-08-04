# ==== FILE 2: services/aiml-orchestration/tests/test_rag_pipeline.py ====

"""
End-to-end RAG pipeline testing.
Comprehensive tests for the complete RAG workflow.
"""

import unittest
import asyncio
import sys
import os
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock

# Add src to path
sys.path.append('/app/src')

from orchestrators.rag_orchestrator import RAGOrchestrator, RAGResult
from orchestrators.retrieval_orchestrator import RetrievalOrchestrator
from orchestrators.response_synthesizer import ResponseSynthesizer
from orchestrators.context_builder import AssembledContext
from orchestrators.query_processor import QueryAnalysis

class TestRAGPipeline(unittest.TestCase):
    """Test complete RAG pipeline functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.rag_orchestrator = RAGOrchestrator()
        self.test_queries = [
            "What is machine learning?",
            "How does artificial intelligence work?",
            "Explain neural networks",
            "What are the benefits of deep learning?",
            "How to implement RAG systems?"
        ]
        
        self.mock_context = AssembledContext(
            context_text="Machine learning is a subset of artificial intelligence that enables computers to learn without being explicitly programmed.",
            total_chunks=2,
            total_tokens=100,
            relevance_score=0.85,
            sources=["AI Textbook", "ML Guide"],
            chunks=[],
            metadata={"test": True}
        )

    def test_rag_orchestrator_initialization(self):
        """Test RAG orchestrator initializes correctly."""
        self.assertIsInstance(self.rag_orchestrator, RAGOrchestrator)
        self.assertEqual(self.rag_orchestrator.config['confidence_threshold'], 0.7)
        self.assertTrue(self.rag_orchestrator.config['enable_web_fallback'])
        self.assertEqual(self.rag_orchestrator.config['default_model'], 'gemma:3b')

    def test_single_query_processing(self):
        """Test processing a single query through RAG pipeline."""
        async def run_test():
            query = "What is machine learning?"
            result = await self.rag_orchestrator.process_query(query)
            
            # Verify result structure
            self.assertIsInstance(result, RAGResult)
            self.assertEqual(result.query, query)
            self.assertIsNotNone(result.retrieval_result)
            self.assertIsNotNone(result.synthesized_response)
            self.assertGreaterEqual(result.confidence, 0.0)
            self.assertLessEqual(result.confidence, 1.0)
            self.assertIsInstance(result.fallback_used, bool)
            self.assertIsNotNone(result.metadata)
            
            return result
        
        # Run async test
        result = asyncio.run(run_test())
        self.assertIsNotNone(result)

    def test_batch_query_processing(self):
        """Test batch processing of multiple queries."""
        async def run_test():
            results = await self.rag_orchestrator.batch_process_queries(self.test_queries)
            
            # Verify all queries processed
            self.assertEqual(len(results), len(self.test_queries))
            
            # Verify each result
            for result in results:
                self.assertIsInstance(result, RAGResult)
                self.assertIn(result.query, self.test_queries)
                self.assertGreaterEqual(result.confidence, 0.0)
                self.assertLessEqual(result.confidence, 1.0)
            
            return results
        
        results = asyncio.run(run_test())
        self.assertGreater(len(results), 0)

    def test_confidence_threshold_fallback(self):
        """Test that low confidence triggers fallback."""
        async def run_test():
            # Process query that should trigger fallback
            query = "Very specific technical question about obscure topic"
            result = await self.rag_orchestrator.process_query(query)
            
            # With no real data, should trigger fallback
            self.assertTrue(result.fallback_used)
            self.assertLess(result.confidence, 0.7)  # Below fallback threshold
            
            return result
        
        result = asyncio.run(run_test())
        self.assertIsNotNone(result)

    def test_rag_pipeline_performance(self):
        """Test RAG pipeline performance metrics."""
        async def run_test():
            start_time = datetime.now()
            query = "What is artificial intelligence?"
            result = await self.rag_orchestrator.process_query(query)
            end_time = datetime.now()
            
            # Verify processing time is reasonable
            processing_time = (end_time - start_time).total_seconds()
            self.assertLess(processing_time, 30.0)  # Should complete within 30 seconds
            self.assertGreater(result.total_processing_time, 0.0)
            
            return result
        
        result = asyncio.run(run_test())
        self.assertIsNotNone(result)

    def test_error_handling(self):
        """Test RAG pipeline error handling."""
        async def run_test():
            # Test with invalid query
            result = await self.rag_orchestrator.process_query("")
            
            # Should handle gracefully
            self.assertIsInstance(result, RAGResult)
            self.assertEqual(result.confidence, 0.0)
            self.assertTrue(result.fallback_used)
            
            return result
        
        result = asyncio.run(run_test())
        self.assertIsNotNone(result)

    def test_rag_statistics_tracking(self):
        """Test that statistics are properly tracked."""
        async def run_test():
            # Get initial stats
            initial_stats = self.rag_orchestrator.get_rag_statistics()
            initial_queries = initial_stats['total_queries']
            
            # Process a query
            await self.rag_orchestrator.process_query("Test query")
            
            # Check updated stats
            updated_stats = self.rag_orchestrator.get_rag_statistics()
            self.assertEqual(updated_stats['total_queries'], initial_queries + 1)
            self.assertGreaterEqual(updated_stats['successful_queries'], initial_stats['successful_queries'])
            
            return updated_stats
        
        stats = asyncio.run(run_test())
        self.assertIsNotNone(stats)

    def test_system_health_monitoring(self):
        """Test system health monitoring."""
        health = self.rag_orchestrator.get_system_health()
        
        # Verify health structure
        self.assertIn('status', health)
        self.assertIn('success_rate', health)
        self.assertIn('average_response_time', health)
        self.assertIn('component_status', health)
        
        # Verify component status
        self.assertIn('retrieval', health['component_status'])
        self.assertIn('synthesis', health['component_status'])
        self.assertIn('workflow', health['component_status'])

    def test_configuration_updates(self):
        """Test configuration updates."""
        original_threshold = self.rag_orchestrator.config['confidence_threshold']
        
        # Update configuration
        new_config = {'confidence_threshold': 0.8}
        self.rag_orchestrator.update_configuration(new_config)
        
        # Verify update
        self.assertEqual(self.rag_orchestrator.config['confidence_threshold'], 0.8)
        
        # Restore original
        self.rag_orchestrator.update_configuration({'confidence_threshold': original_threshold})

    def test_workflow_integration(self):
        """Test workflow manager integration."""
        async def run_test():
            query = "Test workflow integration"
            result = await self.rag_orchestrator.process_query(query)
            
            # Verify workflow metadata exists
            self.assertIn('workflow_id', result.metadata)
            self.assertIn('phases_completed', result.metadata)
            
            # Verify phases
            phases = result.metadata['phases_completed']
            self.assertIn('retrieval', phases)
            self.assertIn('synthesis', phases)
            
            return result
        
        result = asyncio.run(run_test())
        self.assertIsNotNone(result)
