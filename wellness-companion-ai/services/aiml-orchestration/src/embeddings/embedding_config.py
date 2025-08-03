
# File 4: services/aiml-orchestration/src/embeddings/embedding_config.py
"""
Configuration management for embedding models.
"""

import logging
from typing import Dict, Any
import os

logger = logging.getLogger(__name__)

class EmbeddingConfig:
    """Configuration for embedding models and processing"""
    
    DEFAULT_CONFIG = {
        "model": {
            "name": "all-MiniLM-L6-v2",
            "dimensions": 384,
            "max_sequence_length": 256,
            "device": "auto"  # auto, cpu, cuda
        },
        "processing": {
            "batch_size": 32,
            "normalize_embeddings": True,
            "show_progress_bar": False
        },
        "cache": {
            "enabled": True,
            "cache_dir": "/app/cache/embeddings",
            "max_cache_size": "1GB"
        },
        "performance": {
            "num_workers": 1,
            "use_fast_tokenizer": True
        }
    }
    
    def __init__(self, config_dict: Dict[str, Any] = None):
        self.config = self.DEFAULT_CONFIG.copy()
        if config_dict:
            self._update_config(config_dict)
        
        # Override with environment variables
        self._load_from_env()
    
    def _update_config(self, new_config: Dict[str, Any]):
        """Recursively update configuration"""
        for key, value in new_config.items():
            if key in self.config and isinstance(self.config[key], dict):
                self.config[key].update(value)
            else:
                self.config[key] = value
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        env_mappings = {
            "EMBEDDING_MODEL_NAME": ("model", "name"),
            "EMBEDDING_BATCH_SIZE": ("processing", "batch_size"),
            "EMBEDDING_CACHE_ENABLED": ("cache", "enabled"),
            "EMBEDDING_DEVICE": ("model", "device")
        }
        
        for env_var, (section, key) in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                # Type conversion
                if key in ["batch_size", "num_workers"]:
                    value = int(value)
                elif key in ["normalize_embeddings", "enabled", "show_progress_bar"]:
                    value = value.lower() in ["true", "1", "yes"]
                
                self.config[section][key] = value
    
    def get(self, section: str, key: str = None):
        """Get configuration value"""
        if key is None:
            return self.config.get(section, {})
        return self.config.get(section, {}).get(key)
    
    def get_model_config(self) -> Dict:
        """Get model-specific configuration"""
        return self.config["model"]
    
    def get_processing_config(self) -> Dict:
        """Get processing configuration"""
        return self.config["processing"]
