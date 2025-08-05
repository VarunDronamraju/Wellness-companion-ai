"""
Integration Package - Wellness Companion AI
External service integration clients
"""

from .aiml_client import AIMLServiceClient, get_aiml_client, close_aiml_client
from .exceptions import (
    IntegrationException,
    ServiceUnavailableException,
    ServiceTimeoutException,
    ServiceAuthenticationException,
    ServiceValidationException,
    AIMLServiceException
)
from .client_config import get_aiml_config, validate_all_configs

__all__ = [
    # Clients
    "AIMLServiceClient",
    "get_aiml_client", 
    "close_aiml_client",
    
    # Exceptions
    "IntegrationException",
    "ServiceUnavailableException",
    "ServiceTimeoutException", 
    "ServiceAuthenticationException",
    "ServiceValidationException",
    "AIMLServiceException",
    
    # Configuration
    "get_aiml_config",
    "validate_all_configs"
]