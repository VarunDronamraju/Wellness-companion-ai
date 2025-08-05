"""
Core Backend Configuration - Wellness Companion AI
Application constants and derived configuration
"""

from .settings import settings
import logging
from typing import Dict, Any


class CoreBackendConfig:
    """Core Backend application configuration"""
    
    # === SERVICE INFO ===
    SERVICE_NAME = settings.service_name
    VERSION = settings.version
    ENVIRONMENT = settings.environment
    
    # === API METADATA ===
    API_TITLE = "Wellness Companion AI - Core Backend"
    API_DESCRIPTION = """
    Core Backend Service for Wellness Companion AI
    
    This service provides:
    - API Gateway functionality
    - Service orchestration
    - Authentication management
    - Document management
    - Search orchestration
    """
    
    # === DOCUMENTATION URLS ===
    DOCS_URL = "/docs" if settings.debug else None
    REDOC_URL = "/redoc" if settings.debug else None
    
    # === CORS CONFIGURATION ===
    CORS_CONFIG = {
        "allow_origins": settings.cors_origins,
        "allow_credentials": settings.cors_credentials,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": [
            "Content-Type", 
            "Authorization", 
            "X-API-Key", 
            "X-Request-ID",
            "X-User-ID"
        ],
    }
    
    # === EXTERNAL SERVICES ===
    EXTERNAL_SERVICES = {
        "aiml_orchestration": {
            "url": settings.aiml_service_url,
            "timeout": 30,
            "retries": 3
        },
        "data_layer": {
            "url": settings.data_layer_url,
            "timeout": 15,
            "retries": 2
        }
    }
    
    # === LOGGING CONFIGURATION ===
    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s",
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
            "detailed": {
                "formatter": "detailed",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "root": {
            "level": settings.log_level,
            "handlers": ["default"],
        },
    }
    
    @classmethod
    def get_service_info(cls) -> Dict[str, Any]:
        """Get service information for health checks"""
        return {
            "service": cls.SERVICE_NAME,
            "version": cls.VERSION,
            "environment": cls.ENVIRONMENT,
            "debug_mode": settings.debug,
            "api_docs_enabled": bool(cls.DOCS_URL)
        }
    
    @classmethod
    def get_external_service_urls(cls) -> Dict[str, str]:
        """Get external service URLs for client configuration"""
        return {
            service: config["url"] 
            for service, config in cls.EXTERNAL_SERVICES.items()
        }


# Configuration instance
config = CoreBackendConfig()