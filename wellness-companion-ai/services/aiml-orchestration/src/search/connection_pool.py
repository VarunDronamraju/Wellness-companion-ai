
# File 3: services/aiml-orchestration/src/search/connection_pool.py
"""
Connection pool management for Qdrant clients.
"""

import logging
from typing import Dict, Optional
from .qdrant_client import QdrantClientManager
import threading
import time

logger = logging.getLogger(__name__)

class QdrantConnectionPool:
    """Connection pool for Qdrant clients"""
    
    def __init__(self, max_connections: int = 5):
        self.max_connections = max_connections
        self.connections: Dict[str, QdrantClientManager] = {}
        self.connection_lock = threading.Lock()
        self.last_used: Dict[str, float] = {}
        
    def get_connection(self, connection_id: str = "default") -> QdrantClientManager:
        """
        Get a connection from the pool
        
        Args:
            connection_id: Identifier for the connection
            
        Returns:
            QdrantClientManager instance
        """
        with self.connection_lock:
            # Return existing connection if available
            if connection_id in self.connections:
                connection = self.connections[connection_id]
                if connection.connected:
                    self.last_used[connection_id] = time.time()
                    return connection
                else:
                    # Reconnect if disconnected
                    if connection.connect():
                        self.last_used[connection_id] = time.time()
                        return connection
                    else:
                        # Remove failed connection
                        del self.connections[connection_id]
                        del self.last_used[connection_id]
            
            # Create new connection if under limit
            if len(self.connections) < self.max_connections:
                connection = QdrantClientManager()
                if connection.connect():
                    self.connections[connection_id] = connection
                    self.last_used[connection_id] = time.time()
                    logger.info(f"Created new connection: {connection_id}")
                    return connection
                else:
                    raise ConnectionError("Failed to create new Qdrant connection")
            
            # Pool is full, reuse oldest connection
            oldest_id = min(self.last_used.keys(), key=lambda k: self.last_used[k])
            connection = self.connections[oldest_id]
            
            # Move to new ID
            del self.connections[oldest_id]
            del self.last_used[oldest_id]
            
            self.connections[connection_id] = connection
            self.last_used[connection_id] = time.time()
            
            logger.info(f"Reused connection {oldest_id} as {connection_id}")
            return connection
    
    def close_connection(self, connection_id: str):
        """Close and remove a connection"""
        with self.connection_lock:
            if connection_id in self.connections:
                del self.connections[connection_id]
                del self.last_used[connection_id]
                logger.info(f"Closed connection: {connection_id}")
    
    def get_pool_status(self) -> Dict:
        """Get connection pool status"""
        with self.connection_lock:
            return {
                "active_connections": len(self.connections),
                "max_connections": self.max_connections,
                "connection_ids": list(self.connections.keys()),
                "last_used_times": self.last_used.copy()
            }