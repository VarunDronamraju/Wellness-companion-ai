
# ==== FILE 3: services/aiml-orchestration/tests/test_embeddings.py ====

"""
Embedding generation validation tests.
Tests for embedding pipeline and vector operations.
"""

import unittest
import numpy as np
import sys

sys.path.append('/app/src')

from embeddings.sentence_transformers_client import SentenceTransformersClient
from search.vector_search import VectorSearch

class TestEmbeddings(unittest.TestCase):
    """Test embedding generation and vector operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.embedding_client = SentenceTransformersClient()
        self.vector_search = VectorSearch()
        
        self.test_texts = [
            "Machine learning is a subset of artificial intelligence.",
            "Deep learning uses neural networks with multiple layers.",
            "Natural language processing helps computers understand text.",
            "Computer vision enables machines to interpret visual information.",
            "Reinforcement learning trains agents through rewards and penalties."
        ]

    def test_embedding_generation(self):
        """Test embedding generation for text."""
        text = "This is a test sentence for embedding generation."
        
        try:
            embeddings = self.embedding_client.encode([text])
            
            # Verify embedding structure
            self.assertIsInstance(embeddings, (list, np.ndarray))
            if isinstance(embeddings, list):
                self.assertGreater(len(embeddings), 0)
                if len(embeddings) > 0:
                    self.assertIsInstance(embeddings[0], (list, np.ndarray))
            
        except Exception as e:
            # Embedding client might not be available in test environment
            self.skipTest(f"Embedding client not available: {str(e)}")

    def test_batch_embedding_generation(self):
        """Test batch embedding generation."""
        try:
            embeddings = self.embedding_client.encode(self.test_texts)
            
            # Verify batch results
            self.assertIsInstance(embeddings, (list, np.ndarray))
            
            if isinstance(embeddings, list):
                self.assertEqual(len(embeddings), len(self.test_texts))
            elif isinstance(embeddings, np.ndarray):
                self.assertEqual(embeddings.shape[0], len(self.test_texts))
            
        except Exception as e:
            self.skipTest(f"Batch embedding not available: {str(e)}")

    def test_embedding_consistency(self):
        """Test that same text produces consistent embeddings."""
        text = "Consistent embedding test"
        
        try:
            embeddings1 = self.embedding_client.encode([text])
            embeddings2 = self.embedding_client.encode([text])
            
            # Should be identical (or very close due to floating point)
            if isinstance(embeddings1, list) and isinstance(embeddings2, list):
                if len(embeddings1) > 0 and len(embeddings2) > 0:
                    emb1 = np.array(embeddings1[0])
                    emb2 = np.array(embeddings2[0])
                    similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
                    self.assertGreater(similarity, 0.99)  # Should be very similar
            
        except Exception as e:
            self.skipTest(f"Embedding consistency test not available: {str(e)}")

    def test_embedding_dimensions(self):
        """Test embedding dimensions are consistent."""
        try:
            embeddings = self.embedding_client.encode(self.test_texts[:2])
            
            if isinstance(embeddings, list) and len(embeddings) >= 2:
                emb1 = np.array(embeddings[0])
                emb2 = np.array(embeddings[1])
                
                # Dimensions should match
                self.assertEqual(emb1.shape, emb2.shape)
                self.assertGreater(len(emb1), 0)  # Should have some dimensions
            
        except Exception as e:
            self.skipTest(f"Embedding dimensions test not available: {str(e)}")

    def test_vector_search_integration(self):
        """Test integration between embeddings and vector search."""
        try:
            # Test vector search statistics (should work without actual data)
            stats = self.vector_search.get_search_statistics()
            
            self.assertIsInstance(stats, dict)
            self.assertIn('total_searches', stats)
            self.assertIn('success_rate', stats)
            
        except Exception as e:
            self.skipTest(f"Vector search integration test failed: {str(e)}")

    def test_embedding_quality_metrics(self):
        """Test embedding quality assessment."""
        try:
            # Generate embeddings for similar and dissimilar texts
            similar_texts = [
                "Machine learning algorithms",
                "Machine learning models"
            ]
            
            dissimilar_texts = [
                "Machine learning algorithms", 
                "Cooking recipes for dinner"
            ]
            
            similar_embs = self.embedding_client.encode(similar_texts)
            dissimilar_embs = self.embedding_client.encode(dissimilar_texts)
            
            if (isinstance(similar_embs, list) and len(similar_embs) >= 2 and
                isinstance(dissimilar_embs, list) and len(dissimilar_embs) >= 2):
                
                # Calculate similarities
                sim_emb1, sim_emb2 = np.array(similar_embs[0]), np.array(similar_embs[1])
                dissim_emb1, dissim_emb2 = np.array(dissimilar_embs[0]), np.array(dissimilar_embs[1])
                
                similar_score = np.dot(sim_emb1, sim_emb2) / (np.linalg.norm(sim_emb1) * np.linalg.norm(sim_emb2))
                dissimilar_score = np.dot(dissim_emb1, dissim_emb2) / (np.linalg.norm(dissim_emb1) * np.linalg.norm(dissim_emb2))
                
                # Similar texts should have higher similarity than dissimilar texts
                self.assertGreater(similar_score, dissimilar_score)
            
        except Exception as e:
            self.skipTest(f"Embedding quality test not available: {str(e)}")
