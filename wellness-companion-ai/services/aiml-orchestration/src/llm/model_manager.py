
# File 2: services/aiml-orchestration/src/llm/model_manager.py
"""
Model loading, switching, and management for LLM operations.
"""

import logging
from typing import Dict, List, Any, Optional
from .ollama_client import OllamaClient

logger = logging.getLogger(__name__)

class LLMModelManager:
    """Manages LLM models and switching between them"""
    
    SUPPORTED_MODELS = {
        'gemma:3b': {
            'size': '2GB',
            'ram_required': '4GB',
            'description': 'Fast, efficient model for general tasks',
            'use_cases': ['chat', 'qa', 'summarization']
        },
        'mistral:7b': {
            'size': '4.1GB',
            'ram_required': '8GB',
            'description': 'High-quality model with good reasoning',
            'use_cases': ['complex_qa', 'analysis', 'reasoning']
        },
        'llama2:7b': {
            'size': '3.8GB',
            'ram_required': '8GB',
            'description': 'Meta\'s LLaMA 2 model, well-balanced',
            'use_cases': ['general_purpose', 'conversation', 'instruction_following']
        }
    }
    
    def __init__(self):
        self.ollama_client = OllamaClient()
        self.active_model = None
        self.model_cache = {}  # Cache for model performance stats
        
    def initialize(self) -> Dict[str, Any]:
        """Initialize the model manager"""
        try:
            if not self.ollama_client.connect():
                return {
                    'success': False,
                    'error': 'Failed to connect to Ollama service'
                }
            
            # Get available models
            models_result = self.ollama_client.list_models()
            if not models_result['success']:
                return {
                    'success': False,
                    'error': f"Failed to list models: {models_result.get('error', 'Unknown error')}"
                }
            
            available_models = models_result.get('model_names', [])
            logger.info(f"Available models: {available_models}")
            
            # Set default model if available
            for preferred_model in ['gemma:3b', 'mistral:7b', 'llama2:7b']:
                if preferred_model in available_models:
                    self.active_model = preferred_model
                    logger.info(f"Set default model: {preferred_model}")
                    break
            
            return {
                'success': True,
                'available_models': available_models,
                'active_model': self.active_model,
                'supported_models': list(self.SUPPORTED_MODELS.keys())
            }
            
        except Exception as e:
            logger.error(f"Model manager initialization failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def switch_model(self, model_name: str) -> Dict[str, Any]:
        """Switch to a different model"""
        try:
            if model_name not in self.SUPPORTED_MODELS:
                return {
                    'success': False,
                    'error': f'Unsupported model: {model_name}. Supported: {list(self.SUPPORTED_MODELS.keys())}'
                }
            
            # Check if model is available
            models_result = self.ollama_client.list_models()
            if not models_result['success']:
                return {'success': False, 'error': 'Failed to check available models'}
            
            available_models = models_result.get('model_names', [])
            
            if model_name not in available_models:
                return {
                    'success': False,
                    'error': f'Model {model_name} not available. Available: {available_models}',
                    'suggestion': f'Try pulling the model first with pull_model("{model_name}")'
                }
            
            old_model = self.active_model
            self.active_model = model_name
            
            logger.info(f"Switched model: {old_model} → {model_name}")
            
            return {
                'success': True,
                'old_model': old_model,
                'new_model': model_name,
                'model_info': self.SUPPORTED_MODELS[model_name]
            }
            
        except Exception as e:
            logger.error(f"Model switching failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def generate_response(self,
                         prompt: str,
                         system_prompt: Optional[str] = None,
                         model_override: Optional[str] = None,
                         **kwargs) -> Dict[str, Any]:
        """
        Generate response using active or specified model
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            model_override: Override active model for this request
            **kwargs: Additional generation parameters
            
        Returns:
            Generation result
        """
        try:
            model_to_use = model_override or self.active_model
            
            if not model_to_use:
                return {
                    'success': False,
                    'error': 'No active model set. Please switch to a model first.'
                }
            
            result = self.ollama_client.generate_response(
                model=model_to_use,
                prompt=prompt,
                system_prompt=system_prompt,
                **kwargs
            )
            
            # Update model cache with performance stats
            if result['success'] and model_to_use not in self.model_cache:
                self.model_cache[model_to_use] = {
                    'requests_count': 0,
                    'total_processing_time': 0,
                    'average_processing_time': 0
                }
            
            if result['success']:
                cache_entry = self.model_cache[model_to_use]
                cache_entry['requests_count'] += 1
                cache_entry['total_processing_time'] += result.get('processing_time', 0)
                cache_entry['average_processing_time'] = (
                    cache_entry['total_processing_time'] / cache_entry['requests_count']
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Response generation failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get current model status and statistics"""
        try:
            # Get available models
            models_result = self.ollama_client.list_models()
            
            return {
                'success': True,
                'active_model': self.active_model,
                'supported_models': self.SUPPORTED_MODELS,
                'available_models': models_result.get('model_names', []) if models_result['success'] else [],
                'model_cache': self.model_cache,
                'ollama_connected': self.ollama_client.connected
            }
            
        except Exception as e:
            logger.error(f"Get model status failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def pull_model(self, model_name: str) -> Dict[str, Any]:
        """Pull/download a model"""
        if model_name not in self.SUPPORTED_MODELS:
            return {
                'success': False,
                'error': f'Unsupported model: {model_name}'
            }
        
        return self.ollama_client.pull_model(model_name)
