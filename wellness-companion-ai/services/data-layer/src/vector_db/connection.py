# services/data-layer/src/vector_db/connection.py
"""
Database connection management for data layer - FIXED VERSION.
"""

import logging
from typing import Optional
from .qdrant_client import DataLayerQdrantClient
import threading

logger = logging.getLogger(__name__)

class VectorDBConnection:
    """Singleton connection manager for vector database"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.client = None
                    cls._instance.initialized = False
        return cls._instance
    
    def initialize(self) -> bool:
        """Initialize the connection"""
        if self.initialized and self.client and self.client.connected:
            return True
        
        try:
            self.client = DataLayerQdrantClient()
            if self.client.connect():
                self.initialized = True
                logger.info("Vector DB connection initialized")
                return True
            else:
                logger.error("Failed to initialize vector DB connection")
                self.initialized = False
                return False
        except Exception as e:
            logger.error(f"Vector DB initialization error: {str(e)}")
            self.initialized = False
            return False
    
    def get_client(self) -> Optional[DataLayerQdrantClient]:
        """Get the Qdrant client"""
        if not self.initialized or not self.client:
            if not self.initialize():
                return None
        return self.client
    
    def health_check(self) -> bool:
        """Check if connection is healthy - FIXED VERSION"""
        try:
            # Try to initialize if not already done
            if not self.initialized:
                if not self.initialize():
                    return False
            
            # Get client
            client = self.get_client()
            if not client:
                return False
            
            # Check if client is connected
            if not client.connected:
                # Try to reconnect
                if not client.connect():
                    return False
            
            # Test with a simple operation
            collections = client.client.get_collections()
            logger.info("Vector DB health check passed")
            return True
            
        except Exception as e:
            logger.error(f"Vector DB health check failed: {str(e)}")
            return False
    
    def reconnect(self) -> bool:
        """Reconnect to the database"""
        self.initialized = False
        self.client = None
        return self.initialize()