
# File 1: services/aiml-orchestration/src/embeddings/sentence_transformers.py
"""
Sentence Transformers integration with all-MiniLM-L6-v2 model.
"""

import logging
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
import numpy as np
import torch

logger = logging.getLogger(__name__)

class SentenceTransformersManager:
    """Manages Sentence Transformers models for embedding generation"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    def load_model(self) -> bool:
        """
        Load the sentence transformers model
        
        Returns:
            bool: True if model loaded successfully
        """
        try:
            logger.info(f"Loading Sentence Transformer model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name, device=self.device)
            logger.info(f"Model loaded successfully on device: {self.device}")
            return True
        except Exception as e:
            logger.error(f"Failed to load model {self.model_name}: {str(e)}")
            return False
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        if not self.model:
            if not self.load_model():
                raise RuntimeError("Model not loaded and failed to load")
        
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {str(e)}")
            raise
    
    def get_model_info(self) -> Dict:
        """Get model information"""
        if not self.model:
            return {"status": "not_loaded"}
        
        return {
            "model_name": self.model_name,
            "device": self.device,
            "max_seq_length": self.model.max_seq_length,
            "embedding_dimension": self.model.get_sentence_embedding_dimension(),
            "status": "loaded"
        }