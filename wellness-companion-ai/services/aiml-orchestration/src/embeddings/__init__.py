
# File 5: services/aiml-orchestration/src/embeddings/__init__.py
"""
Embeddings Module
Sentence transformers integration, embedding generation, and model management.
"""

from .model_manager import EmbeddingModelManager
from .sentence_transformers import SentenceTransformersManager
from .embedding_config import EmbeddingConfig

__all__ = [
    'EmbeddingModelManager',
    'SentenceTransformersManager', 
    'EmbeddingConfig'
]