"""
Core Backend Main Application - Wellness Companion AI
C:\Users\varun\Desktop\JObSearch\Application\WellnessAtWorkAI\wellness-companion-ai\services\core-backend\src\api\main.py
FastAPI application instance and basic endpoints
"""

from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from datetime import datetime
import logging

from .app_factory import create_application
from .router import router as api_router
from ..core.dependencies import get_current_settings, get_service_config, log_request_info
from ..core.config import config

logger = logging.getLogger(__name__)

# Create FastAPI application using factory
app = create_application()

# Include main API router
app.include_router(api_router)


# === ROOT ENDPOINTS ===

@app.get("/", tags=["root"])
async def root(
    request_info: dict = Depends(log_request_info),
    service_config = Depends(get_service_config)
):
    """Root endpoint with service information"""
    return {
        "service": service_config.SERVICE_NAME,
        "version": service_config.VERSION,
        "environment": service_config.ENVIRONMENT,
        "status": "running",
        "message": "Wellness Companion AI - Core Backend Service",
        "timestamp": datetime.utcnow().isoformat(),
        "request_id": request_info["request_id"],
        "documentation": {
            "swagger_ui": "/docs" if service_config.DOCS_URL else "disabled",
            "redoc": "/redoc" if service_config.REDOC_URL else "disabled"
        }
    }


@app.get("/ping", tags=["health"])
async def ping():
    """Simple ping endpoint for uptime monitoring"""
    return {
        "message": "pong",
        "timestamp": datetime.utcnow().isoformat(),
        "service": config.SERVICE_NAME
    }


@app.get("/version", tags=["system"])
async def get_version():
    """Get service version information"""
    return {
        "service": config.SERVICE_NAME,
        "version": config.VERSION,
        "environment": config.ENVIRONMENT,
        "build_info": {
            "python_version": "3.11+",
            "fastapi_version": "0.104.1+",
            "framework": "FastAPI"
        }
    }


# === PLACEHOLDER ENDPOINTS (will be replaced in subsequent tasks) ===

@app.get("/api/status", tags=["system"])
async def get_detailed_status(settings = Depends(get_current_settings)):
    """Detailed service status - enhanced in Task 38"""
    return {
        "service_info": config.get_service_info(),
        "environment": {
            "aiml_service_url": settings.aiml_service_url,
            "data_layer_url": settings.data_layer_url,
            "redis_configured": bool(settings.redis_url),
            "jwt_configured": bool(settings.jwt_secret_key),
            "google_oauth_configured": bool(settings.google_client_id),
            "aws_cognito_configured": bool(settings.aws_cognito_user_pool_id)
        },
        "external_services": config.get_external_service_urls(),
        "capabilities": [
            "api_gateway",
            "service_orchestration", 
            "request_validation",
            "cors_handling"
        ],
        "planned_features": [
            "health_monitoring (Task 38)",
            "authentication (Phase 6)",
            "document_management (Tasks 40-43)",
            "search_orchestration (Tasks 39, 44-45)",
            "rate_limiting (Task 73)"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }


# === DEVELOPMENT HELPER ENDPOINTS ===

@app.get("/api/config", tags=["system"])
async def get_configuration(settings = Depends(get_current_settings)):
    """Get current configuration (development only)"""
    if config.ENVIRONMENT == "production":
        return JSONResponse(
            status_code=403,
            content={"error": "Configuration endpoint disabled in production"}
        )
    
    return {
        "cors_origins": settings.cors_origins,
        "debug_mode": settings.debug,
        "external_services": config.get_external_service_urls(),
        "api_prefix": settings.api_v1_prefix,
        "max_upload_size": settings.max_upload_size,
        "log_level": settings.log_level
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8001,  # Fixed: Use port 8001
        reload=True
    )