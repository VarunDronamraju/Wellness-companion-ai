
# File 4: services/data-layer/src/vector_db/qdrant_client.py
"""
Qdrant operations for data layer service.
"""

import logging
from typing import List, Dict, Optional, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
import os
import uuid

logger = logging.getLogger(__name__)

class DataLayerQdrantClient:
    """Qdrant client for data layer operations (CRUD)"""
    
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
            logger.info(f"Data layer connected to Qdrant at {self.url}")
            return True
        except Exception as e:
            logger.error(f"Data layer failed to connect to Qdrant: {str(e)}")
            self.connected = False
            return False
    
    def create_collection(self, 
                         collection_name: str,
                         vector_size: int = 384,
                         distance: str = "Cosine") -> bool:
        """
        Create a new collection
        
        Args:
            collection_name: Name of the collection
            vector_size: Dimension of vectors
            distance: Distance metric (Cosine, Dot, Euclid)
            
        Returns:
            bool: True if successful
        """
        if not self.connected and not self.connect():
            raise ConnectionError("Not connected to Qdrant")
        
        try:
            distance_map = {
                "Cosine": Distance.COSINE,
                "Dot": Distance.DOT,
                "Euclid": Distance.EUCLID
            }
            
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=distance_map.get(distance, Distance.COSINE)
                )
            )
            
            logger.info(f"Created collection: {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create collection {collection_name}: {str(e)}")
            return False
    
    def upsert_vectors(self,
                      collection_name: str,
                      vectors: List[List[float]],
                      payloads: List[Dict],
                      ids: List[str] = None) -> bool:
        """
        Insert or update vectors
        
        Args:
            collection_name: Target collection
            vectors: List of vector embeddings
            payloads: List of metadata for each vector
            ids: Optional list of IDs (auto-generated if None)
            
        Returns:
            bool: True if successful
        """
        if not self.connected and not self.connect():
            raise ConnectionError("Not connected to Qdrant")
        
        try:
            # Generate IDs if not provided
            if ids is None:
                ids = [str(uuid.uuid4()) for _ in vectors]
            
            # Create points
            points = [
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload
                )
                for point_id, vector, payload in zip(ids, vectors, payloads)
            ]
            
            # Upsert points
            self.client.upsert(
                collection_name=collection_name,
                points=points
            )
            
            logger.info(f"Upserted {len(points)} vectors to {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upsert vectors: {str(e)}")
            return False
    
    def delete_vectors(self,
                      collection_name: str,
                      ids: List[str] = None,
                      filter_condition: Dict = None) -> bool:
        """
        Delete vectors by IDs or filter
        
        Args:
            collection_name: Target collection
            ids: List of IDs to delete
            filter_condition: Filter condition for deletion
            
        Returns:
            bool: True if successful
        """
        if not self.connected and not self.connect():
            raise ConnectionError("Not connected to Qdrant")
        
        try:
            if ids:
                self.client.delete(
                    collection_name=collection_name,
                    points_selector=ids
                )
                logger.info(f"Deleted {len(ids)} vectors from {collection_name}")
            elif filter_condition:
                # Implement filter-based deletion
                self.client.delete(
                    collection_name=collection_name,
                    points_selector=Filter(**filter_condition)
                )
                logger.info(f"Deleted vectors with filter from {collection_name}")
            else:
                logger.warning("No IDs or filter provided for deletion")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete vectors: {str(e)}")
            return False