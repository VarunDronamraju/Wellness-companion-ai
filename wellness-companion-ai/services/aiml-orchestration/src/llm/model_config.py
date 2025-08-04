
# File 4: services/aiml-orchestration/src/llm/model_config.py
"""
Model configurations and settings management.
"""

import logging
from typing import Dict, Any, Optional, List
import os
import json

logger = logging.getLogger(__name__)

class ModelConfig:
    """Configuration management for LLM models"""
    
    DEFAULT_CONFIGS = {
        'generation': {
            'temperature': 0.7,
            'max_tokens': 2048,
            'top_p': 0.9,
            'frequency_penalty': 0.0,
            'presence_penalty': 0.0
        },
        'chat': {
            'temperature': 0.8,
            'max_tokens': 1024,
            'top_p': 0.95
        },
        'summarization': {
            'temperature': 0.3,
            'max_tokens': 512,
            'top_p': 0.8
        },
        'qa': {
            'temperature': 0.1,
            'max_tokens': 256,
            'top_p': 0.7
        }
    }
    
    MODEL_SPECIFIC_CONFIGS = {
        'gemma:3b': {
            'optimal_temperature': 0.7,
            'recommended_max_tokens': 1024,
            'best_use_cases': ['chat', 'qa', 'summarization'],
            'context_window': 2048
        },
        'mistral:7b': {
            'optimal_temperature': 0.6,
            'recommended_max_tokens': 2048,
            'best_use_cases': ['analysis', 'reasoning', 'complex_qa'],
            'context_window': 4096
        },
        'llama2:7b': {
            'optimal_temperature': 0.7,
            'recommended_max_tokens': 1536,
            'best_use_cases': ['general_purpose', 'conversation', 'instruction_following'],
            'context_window': 2048
        }
    }
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self.custom_configs = {}
        self.load_custom_configs()
    
    def load_custom_configs(self):
        """Load custom configurations from file"""
        if not self.config_file or not os.path.exists(self.config_file):
            return
        
        try:
            with open(self.config_file, 'r') as f:
                self.custom_configs = json.load(f)
            logger.info(f"Loaded custom configs from {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to load custom configs: {str(e)}")
    
    def save_custom_configs(self) -> bool:
        """Save custom configurations to file"""
        if not self.config_file:
            return False
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.custom_configs, f, indent=2)
            logger.info(f"Saved custom configs to {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save custom configs: {str(e)}")
            return False
    
    def get_config_for_task(self, task_type: str, model_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get configuration for a specific task type and model
        
        Args:
            task_type: Type of task (generation, chat, summarization, qa)
            model_name: Optional model name for model-specific configs
            
        Returns:
            Configuration dictionary
        """
        # Start with default config for task type
        config = self.DEFAULT_CONFIGS.get(task_type, self.DEFAULT_CONFIGS['generation']).copy()
        
        # Apply model-specific optimizations
        if model_name and model_name in self.MODEL_SPECIFIC_CONFIGS:
            model_config = self.MODEL_SPECIFIC_CONFIGS[model_name]
            
            if 'optimal_temperature' in model_config:
                config['temperature'] = model_config['optimal_temperature']
            
            if 'recommended_max_tokens' in model_config:
                config['max_tokens'] = min(
                    config.get('max_tokens', 2048),
                    model_config['recommended_max_tokens']
                )
        
        # Apply custom overrides
        custom_key = f"{task_type}_{model_name}" if model_name else task_type
        if custom_key in self.custom_configs:
            config.update(self.custom_configs[custom_key])
        
        return config
    
    def set_custom_config(self, task_type: str, model_name: Optional[str], config: Dict[str, Any]):
        """Set custom configuration for a task and model combination"""
        custom_key = f"{task_type}_{model_name}" if model_name else task_type
        self.custom_configs[custom_key] = config
        logger.info(f"Set custom config for {custom_key}")
    
    def get_model_recommendations(self, model_name: str) -> Dict[str, Any]:
        """Get recommendations for a specific model"""
        if model_name not in self.MODEL_SPECIFIC_CONFIGS:
            return {
                'model': model_name,
                'recommendations': 'No specific recommendations available',
                'use_default_configs': True
            }
        
        model_config = self.MODEL_SPECIFIC_CONFIGS[model_name]
        
        return {
            'model': model_name,
            'optimal_temperature': model_config.get('optimal_temperature', 0.7),
            'recommended_max_tokens': model_config.get('recommended_max_tokens', 1024),
            'best_use_cases': model_config.get('best_use_cases', []),
            'context_window': model_config.get('context_window', 2048),
            'performance_tips': self._get_performance_tips(model_name)
        }
    
    def _get_performance_tips(self, model_name: str) -> List[str]:
        """Get performance tips for a specific model"""
        tips = [
            "Use lower temperature (0.1-0.3) for factual tasks",
            "Use higher temperature (0.7-0.9) for creative tasks",
            "Keep prompts concise for better performance"
        ]
        
        if model_name == 'gemma:3b':
            tips.extend([
                "Optimal for quick responses and simple tasks",
                "Keep context under 1500 tokens for best performance",
                "Works well with direct, specific prompts"
            ])
        elif model_name == 'mistral:7b':
            tips.extend([
                "Excellent for complex reasoning tasks",
                "Can handle longer contexts effectively",
                "Benefits from detailed system prompts"
            ])
        elif model_name == 'llama2:7b':
            tips.extend([
                "Well-balanced for most general tasks",
                "Good instruction-following capabilities",
                "Responds well to conversational prompts"
            ])
        
        return tips
    
    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration parameters"""
        validation_result = {
            'valid': True,
            'warnings': [],
            'errors': []
        }
        
        # Temperature validation
        if 'temperature' in config:
            temp = config['temperature']
            if not 0.0 <= temp <= 1.0:
                validation_result['errors'].append(
                    f"Temperature {temp} out of range [0.0, 1.0]"
                )
                validation_result['valid'] = False
            elif temp > 0.9:
                validation_result['warnings'].append(
                    "High temperature (>0.9) may produce unpredictable results"
                )
        
        # Max tokens validation
        if 'max_tokens' in config:
            max_tokens = config['max_tokens']
            if max_tokens <= 0:
                validation_result['errors'].append(
                    f"Max tokens {max_tokens} must be positive"
                )
                validation_result['valid'] = False
            elif max_tokens > 4096:
                validation_result['warnings'].append(
                    "High max_tokens (>4096) may cause memory issues"
                )
        
        # Top-p validation
        if 'top_p' in config:
            top_p = config['top_p']
            if not 0.0 <= top_p <= 1.0:
                validation_result['errors'].append(
                    f"Top-p {top_p} out of range [0.0, 1.0]"
                )
                validation_result['valid'] = False
        
        return validation_result
    
    def get_all_configs(self) -> Dict[str, Any]:
        """Get all available configurations"""
        return {
            'default_configs': self.DEFAULT_CONFIGS,
            'model_specific_configs': self.MODEL_SPECIFIC_CONFIGS,
            'custom_configs': self.custom_configs,
            'supported_models': list(self.MODEL_SPECIFIC_CONFIGS.keys()),
            'supported_tasks': list(self.DEFAULT_CONFIGS.keys())
        }