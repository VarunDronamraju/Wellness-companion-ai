"""
Application Factory - Wellness Companion AI
Factory pattern for creating FastAPI applications
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging.config
from datetime import datetime
from typing import Optional
from src.integrations import close_aiml_client
from src.core.config import config, CoreBackendConfig
from src.core.settings import settings
from .middleware.cors_middleware import setup_cors, validate_cors_config

logger = logging.getLogger(__name__)


def create_application() -> FastAPI:
    """Create and configure FastAPI application"""
    
    # Configure logging
    logging.config.dictConfig(config.LOGGING_CONFIG)
    logger.info("🚀 Creating Core Backend FastAPI application...")
    
    # Validate configuration
    if not validate_cors_config():
        raise ValueError("Invalid CORS configuration")
    
    # Create FastAPI app
    app = FastAPI(
        title=config.API_TITLE,
        description=config.API_DESCRIPTION,
        version=config.VERSION,
        docs_url=config.DOCS_URL,
        redoc_url=config.REDOC_URL,
        openapi_tags=[
            {
                "name": "health",
                "description": "Health check and service status operations"
            },
            {
                "name": "auth", 
                "description": "Authentication and authorization (Phase 6)"
            },
            {
                "name": "documents",
                "description": "Document management operations (Phase 4)"
            },
            {
                "name": "search",
                "description": "Search and knowledge retrieval (Phase 4)"
            },
            {
                "name": "system",
                "description": "System administration and monitoring"
            }
        ]
    )
    
    # Setup middleware
    setup_cors(app)
    
    # Setup exception handlers
    setup_exception_handlers(app)
    
    # Setup event handlers
    setup_event_handlers(app)
    
    logger.info("✅ Core Backend FastAPI application created successfully")
    return app


def setup_exception_handlers(app: FastAPI) -> None:
    """Setup custom exception handlers"""
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request, exc):
        """Handle HTTP exceptions"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.status_code,
                    "message": exc.detail,
                    "timestamp": datetime.utcnow().isoformat(),
                    "path": str(request.url.path)
                }
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        """Handle request validation errors"""
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": 422,
                    "message": "Validation error",
                    "details": exc.errors(),
                    "timestamp": datetime.utcnow().isoformat(),
                    "path": str(request.url.path)
                }
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        """Handle unexpected exceptions"""
        logger.error(f"Unexpected error: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": 500,
                    "message": "Internal server error",
                    "timestamp": datetime.utcnow().isoformat(),
                    "path": str(request.url.path)
                }
            }
        )


def setup_event_handlers(app: FastAPI) -> None:
    """Setup application lifecycle event handlers"""
    
    @app.on_event("startup")
    async def startup_event():
        """Application startup event"""
        logger.info("🚀 Core Backend service starting up...")
        
        # Log configuration
        logger.info(f"Environment: {settings.environment}")
        logger.info(f"Debug mode: {settings.debug}")
        logger.info(f"Service port: {settings.port}")
        logger.info(f"CORS origins: {settings.cors_origins}")
        logger.info(f"AI/ML service: {settings.aiml_service_url}")
        
        # Validate external service URLs
        external_services = config.get_external_service_urls()
        for service, url in external_services.items():
            logger.info(f"External service '{service}': {url}")
        
        logger.info("✅ Core Backend service startup completed")
    

    @app.on_event("shutdown")
    async def shutdown_event():
        """Application shutdown event"""
        logger.info("🔄 Core Backend service shutting down...")
        
        # Cleanup operations
        try:
            # Close AI/ML service client
            await close_aiml_client()
            logger.info("✅ AI/ML service client closed")
            
            # Additional cleanup operations would go here
            # - Close database connections
            # - Close other HTTP client sessions
            # - Flush logs
            
        except Exception as e:
            logger.error(f"Error during shutdown cleanup: {e}")
    
    logger.info("✅ Core Backend service shutdown completed")

# Application instance
def get_application() -> FastAPI:
    """Get configured FastAPI application instance"""
    return create_application()