"""
CORS Middleware - Wellness Companion AI
Cross-Origin Resource Sharing configuration
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ..core.config import config
import logging

logger = logging.getLogger(__name__)


def setup_cors(app: FastAPI) -> None:
    """Configure CORS middleware for the FastAPI application"""
    
    logger.info("Configuring CORS middleware...")
    logger.info(f"Allowed origins: {config.CORS_CONFIG['allow_origins']}")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.CORS_CONFIG["allow_origins"],
        allow_credentials=config.CORS_CONFIG["allow_credentials"],
        allow_methods=config.CORS_CONFIG["allow_methods"],
        allow_headers=config.CORS_CONFIG["allow_headers"],
        expose_headers=[
            "X-Request-ID",
            "X-Response-Time",
            "X-Rate-Limit-Remaining"
        ]
    )
    
    logger.info("✅ CORS middleware configured successfully")


def validate_cors_config() -> bool:
    """Validate CORS configuration"""
    try:
        origins = config.CORS_CONFIG["allow_origins"]
        
        # Check for wildcard in production
        if config.ENVIRONMENT == "production" and "*" in origins:
            logger.warning("⚠️  Wildcard CORS origin detected in production!")
            return False
        
        # Validate origin URLs
        for origin in origins:
            if not origin.startswith(("http://", "https://")):
                logger.error(f"❌ Invalid CORS origin format: {origin}")
                return False
        
        logger.info("✅ CORS configuration validated")
        return True
        
    except Exception as e:
        logger.error(f"❌ CORS configuration validation failed: {e}")
        return False