
"""
Language Model Module
Ollama client integration, model management, prompt engineering, and response handling.
"""

from .ollama_client import OllamaClient
from .model_manager import LLMModelManager
from .connection_handler import OllamaConnectionHandler
from .model_config import ModelConfig
from .prompt_templates import (
    RAG_SYSTEM_PROMPT,
    FALLBACK_SYSTEM_PROMPT,
    STREAMING_SYSTEM_PROMPT,
    RAG_TEMPLATE,
    FALLBACK_TEMPLATE,
    SUMMARIZATION_TEMPLATE,
    COMPARISON_TEMPLATE,
    ANALYSIS_TEMPLATE,
    HIGH_CONFIDENCE_PHRASES,
    LOW_CONFIDENCE_PHRASES,
    UNCERTAINTY_PHRASES
)
from .response_handler import ResponseHandler
from .streaming_handler import StreamingHandler, StreamChunk

__all__ = [
    'OllamaClient',
    'LLMModelManager',
    'OllamaConnectionHandler',
    'ModelConfig',
    'RAG_SYSTEM_PROMPT',
    'FALLBACK_SYSTEM_PROMPT',
    'STREAMING_SYSTEM_PROMPT',
    'RAG_TEMPLATE',
    'FALLBACK_TEMPLATE',
    'SUMMARIZATION_TEMPLATE',
    'COMPARISON_TEMPLATE',
    'ANALYSIS_TEMPLATE',
    'HIGH_CONFIDENCE_PHRASES',
    'LOW_CONFIDENCE_PHRASES',
    'UNCERTAINTY_PHRASES',
    'ResponseHandler',
    'StreamingHandler',
    'StreamChunk'
]
