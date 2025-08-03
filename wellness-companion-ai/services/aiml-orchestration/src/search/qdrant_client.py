
# File 1: services/aiml-orchestration/src/search/qdrant_client.py
"""
Qdrant operations wrapper for AI/ML service.
"""

import logging
from typing import List, Dict, Optional, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter
import os

logger = logging.getLogger(__name__)

class QdrantClientManager:
    """Qdrant client for AI/ML service operations"""
    
    def __init__(self):
        self.client = None
        self.url = os.getenv("QDRANT_URL", "http://qdrant:6333")
        self.connected = False
        
    def connect(self) -> bool:
        """Connect to Qdrant server"""
        try:
            self.client = QdrantClient(url=self.url)
            # Test connection
            collections = self.client.get_collections()
            self.connected = True
            logger.info(f"Connected to Qdrant at {self.url}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {str(e)}")
            self.connected = False
            return False
    
    def search_vectors(self, 
                      collection_name: str,
                      query_vector: List[float],
                      limit: int = 10,
                      score_threshold: float = 0.0) -> List[Dict]:
        """
        Search for similar vectors
        
        Args:
            collection_name: Name of collection to search
            query_vector: Query vector for similarity search
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            
        Returns:
            List of search results with scores and metadata
        """
        if not self.connected and not self.connect():
            raise ConnectionError("Not connected to Qdrant")
        
        try:
            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold
            )
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'id': result.id,
                    'score': result.score,
                    'payload': result.payload,
                    'vector': result.vector
                })
            
            logger.info(f"Found {len(formatted_results)} results in {collection_name}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Vector search failed: {str(e)}")
            raise
    
    def get_collection_info(self, collection_name: str) -> Dict:
        """Get information about a collection"""
        if not self.connected and not self.connect():
            raise ConnectionError("Not connected to Qdrant")
        
        try:
            info = self.client.get_collection(collection_name)
            return {
                'name': collection_name,
                'status': info.status.value,
                'points_count': info.points_count,
                'vector_size': info.config.params.vectors.size,
                'distance_function': info.config.params.vectors.distance.value
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {str(e)}")
            raise
    
    def list_collections(self) -> List[str]:
        """List all available collections"""
        if not self.connected and not self.connect():
            raise ConnectionError("Not connected to Qdrant")
        
        try:
            collections = self.client.get_collections()
            return [col.name for col in collections.collections]
        except Exception as e:
            logger.error(f"Failed to list collections: {str(e)}")
            raise