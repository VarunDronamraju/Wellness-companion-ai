
# File 2: services/aiml-orchestration/src/embeddings/model_manager.py
"""
Model loading, switching, and management for embeddings.
"""

import logging
from typing import Dict, List, Optional
from .sentence_transformers import SentenceTransformersManager

logger = logging.getLogger(__name__)

class EmbeddingModelManager:
    """Manages multiple embedding models and switching between them"""
    
    SUPPORTED_MODELS = {
        "all-MiniLM-L6-v2": {"dimensions": 384, "description": "Fast, efficient, good quality"},
        "all-MiniLM-L12-v2": {"dimensions": 384, "description": "Better quality, slower"},
        "all-mpnet-base-v2": {"dimensions": 768, "description": "High quality, larger"}
    }
    
    def __init__(self):
        self.active_model = None
        self.loaded_models = {}
        self.current_model_name = None
    
    def load_model(self, model_name: str = "all-MiniLM-L6-v2") -> bool:
        """
        Load and set active embedding model
        
        Args:
            model_name: Name of the model to load
            
        Returns:
            bool: True if successful
        """
        if model_name not in self.SUPPORTED_MODELS:
            logger.error(f"Unsupported model: {model_name}")
            return False
        
        try:
            if model_name not in self.loaded_models:
                manager = SentenceTransformersManager(model_name)
                if manager.load_model():
                    self.loaded_models[model_name] = manager
                else:
                    return False
            
            self.active_model = self.loaded_models[model_name]
            self.current_model_name = model_name
            logger.info(f"Switched to model: {model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {str(e)}")
            return False
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using active model"""
        if not self.active_model:
            if not self.load_model():
                raise RuntimeError("No model available")
        
        return self.active_model.generate_embeddings(texts)
    
    def get_status(self) -> Dict:
        """Get manager status"""
        return {
            "active_model": self.current_model_name,
            "loaded_models": list(self.loaded_models.keys()),
            "supported_models": self.SUPPORTED_MODELS,
            "model_info": self.active_model.get_model_info() if self.active_model else None
        }
