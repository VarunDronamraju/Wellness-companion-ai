
# File 3: services/aiml-orchestration/src/embeddings/multi_model_ensemble.py
"""
Multiple embedding models ensemble for improved performance.
"""

import logging
from typing import List, Dict, Optional
import numpy as np
from .model_manager import EmbeddingModelManager

logger = logging.getLogger(__name__)

class MultiModelEnsemble:
    """Ensemble of multiple embedding models for better performance"""
    
    def __init__(self, models: List[str] = None):
        if models is None:
            models = ["all-MiniLM-L6-v2"]  # Default to single model
        
        self.ensemble_models = models
        self.model_managers = {}
        self.weights = None
        
    def initialize_ensemble(self) -> bool:
        """Initialize all models in the ensemble"""
        try:
            for model_name in self.ensemble_models:
                manager = EmbeddingModelManager()
                if manager.load_model(model_name):
                    self.model_managers[model_name] = manager
                else:
                    logger.warning(f"Failed to load ensemble model: {model_name}")
            
            # Set equal weights for all models
            num_models = len(self.model_managers)
            self.weights = [1.0 / num_models] * num_models
            
            logger.info(f"Initialized ensemble with {num_models} models")
            return len(self.model_managers) > 0
            
        except Exception as e:
            logger.error(f"Failed to initialize ensemble: {str(e)}")
            return False
    
    def generate_ensemble_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using ensemble of models"""
        if not self.model_managers:
            if not self.initialize_ensemble():
                raise RuntimeError("Failed to initialize ensemble")
        
        try:
            all_embeddings = []
            
            for model_name, manager in self.model_managers.items():
                embeddings = manager.generate_embeddings(texts)
                all_embeddings.append(np.array(embeddings))
            
            # Weighted average of embeddings
            weighted_embeddings = np.zeros_like(all_embeddings[0])
            for i, embeddings in enumerate(all_embeddings):
                weighted_embeddings += self.weights[i] * embeddings
            
            return weighted_embeddings.tolist()
            
        except Exception as e:
            logger.error(f"Ensemble embedding failed: {str(e)}")
            raise
