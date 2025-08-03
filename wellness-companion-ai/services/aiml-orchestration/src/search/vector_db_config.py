
# File 2: services/aiml-orchestration/src/search/vector_db_config.py
"""
Vector database configuration for AI/ML service.
"""

import logging
from typing import Dict, Any
import os

logger = logging.getLogger(__name__)

class VectorDBConfig:
    """Configuration for vector database operations"""
    
    DEFAULT_CONFIG = {
        "qdrant": {
            "url": "http://qdrant:6333",
            "timeout": 30,
            "retry_attempts": 3,
            "collections": {
                "documents": {
                    "vector_size": 384,
                    "distance": "Cosine"
                },
                "conversations": {
                    "vector_size": 384,
                    "distance": "Cosine"
                },
                "web_cache": {
                    "vector_size": 384,
                    "distance": "Cosine"
                }
            }
        },
        "search": {
            "default_limit": 10,
            "max_limit": 100,
            "default_threshold": 0.7,
            "min_threshold": 0.0
        }
    }
    
    def __init__(self):
        self.config = self.DEFAULT_CONFIG.copy()
        self._load_from_env()
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        qdrant_url = os.getenv("QDRANT_URL")
        if qdrant_url:
            self.config["qdrant"]["url"] = qdrant_url
        
        # Load search thresholds
        threshold = os.getenv("VECTOR_SEARCH_THRESHOLD")
        if threshold:
            try:
                self.config["search"]["default_threshold"] = float(threshold)
            except ValueError:
                logger.warning(f"Invalid threshold value: {threshold}")
    
    def get_qdrant_config(self) -> Dict[str, Any]:
        """Get Qdrant-specific configuration"""
        return self.config["qdrant"]
    
    def get_search_config(self) -> Dict[str, Any]:
        """Get search configuration"""
        return self.config["search"]
    
    def get_collection_config(self, collection_name: str) -> Dict[str, Any]:
        """Get configuration for specific collection"""
        return self.config["qdrant"]["collections"].get(collection_name, {})