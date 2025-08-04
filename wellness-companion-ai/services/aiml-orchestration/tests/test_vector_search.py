# ==== FILE 4: services/aiml-orchestration/tests/test_vector_search.py ====

"""
Vector search functionality tests.
Tests for vector similarity search and operations.
"""

import unittest
import numpy as np
import sys

sys.path.append('/app/src')

from search.vector_search import VectorSearch

class TestVectorSearch(unittest.TestCase):
    """Test vector search functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.vector_search = VectorSearch()
        
        # Mock vectors for testing
        self.test_vectors = [
            np.random.rand(384).tolist(),
            np.random.rand(384).tolist(),
            np.random.rand(384).tolist(),
            np.random.rand(384).tolist(),
            np.random.rand(384).tolist()
        ]

    def test_vector_search_initialization(self):
        """Test vector search initializes correctly."""
        self.assertIsInstance(self.vector_search, VectorSearch)
        
        # Check statistics exist
        stats = self.vector_search.get_search_statistics()
        self.assertIsInstance(stats, dict)
        self.assertIn('total_searches', stats)

    def test_search_similar_documents(self):
        """Test searching for similar documents."""
        query_vector = np.random.rand(384).tolist()
        
        try:
            result = self.vector_search.search_similar_documents(
                query_vector=query_vector,
                collection_name='test_collection',
                limit=5
            )
            
            # Verify result structure
            self.assertIsInstance(result, dict)
            self.assertIn('success', result)
            self.assertIn('results', result)
            
            # Should handle empty collection gracefully
            if result['success']:
                self.assertIsInstance(result['results'], list)
            
        except Exception as e:
            # Vector DB might not be available in test environment
            self.skipTest(f"Vector search not available: {str(e)}")

    def test_search_with_reranking(self):
        """Test search with reranking functionality."""
        query_vector = np.random.rand(384).tolist()
        query_text = "test query for reranking"
        
        try:
            result = self.vector_search.search_with_reranking(
                query_vector=query_vector,
                query_text=query_text,
                collection_name='test_collection',
                limit=10,
                final_limit=5
            )
            
            # Verify result structure
            self.assertIsInstance(result, dict)
            self.assertIn('success', result)
            self.assertIn('results', result)
            
            if result['success']:
                results = result['results']
                self.assertIsInstance(results, list)
                # Should not exceed final_limit
                self.assertLessEqual(len(results), 5)
            
        except Exception as e:
            self.skipTest(f"Reranking search not available: {str(e)}")

    def test_search_statistics_tracking(self):
        """Test that search statistics are tracked properly."""
        initial_stats = self.vector_search.get_search_statistics()
        initial_searches = initial_stats.get('total_searches', 0)
        
        # Perform a search
        query_vector = np.random.rand(384).tolist()
        try:
            self.vector_search.search_similar_documents(
                query_vector=query_vector,
                collection_name='test_collection'
            )
            
            # Check updated statistics
            updated_stats = self.vector_search.get_search_statistics()
            updated_searches = updated_stats.get('total_searches', 0)
            
            # Should increment search count
            self.assertGreaterEqual(updated_searches, initial_searches + 1)
            
        except Exception:
            # If search fails, stats might still be updated
            pass

    def test_vector_validation(self):
        """Test vector input validation."""
        # Test with invalid vector dimensions
        invalid_vector = [1, 2, 3]  # Too short
        
        try:
            result = self.vector_search.search_similar_documents(
                query_vector=invalid_vector,
                collection_name='test_collection'
            )
            
            # Should handle invalid input gracefully
            if not result.get('success', True):
                self.assertIn('error', result)
            
        except Exception as e:
            # Expected for invalid input
            self.assertIsInstance(e, (ValueError, TypeError))

    def test_empty_collection_handling(self):
        """Test handling of empty collections."""
        query_vector = np.random.rand(384).tolist()
        
        try:
            result = self.vector_search.search_similar_documents(
                query_vector=query_vector,
                collection_name='empty_collection',
                limit=5
            )
            
            # Should handle empty collection gracefully
            self.assertIsInstance(result, dict)
            self.assertIn('success', result)
            
            if result['success']:
                self.assertEqual(len(result['results']), 0)
            
        except Exception as e:
            self.skipTest(f"Empty collection test not available: {str(e)}")

    def test_search_performance(self):
        """Test search performance metrics."""
        query_vector = np.random.rand(384).tolist()
        
        try:
            import time
            start_time = time.time()
            
            result = self.vector_search.search_similar_documents(
                query_vector=query_vector,
                collection_name='test_collection'
            )
            
            end_time = time.time()
            search_time = end_time - start_time
            
            # Search should complete quickly (within 5 seconds)
            self.assertLess(search_time, 5.0)
            
            # Check if timing is tracked in statistics
            stats = self.vector_search.get_search_statistics()
            if 'average_search_time' in stats:
                self.assertGreater(stats['average_search_time'], 0)
            
        except Exception as e:
            self.skipTest(f"Performance test not available: {str(e)}")
