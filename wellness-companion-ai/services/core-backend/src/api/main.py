# ========================================
# services/core-backend/src/api/main.py - WORKING VERSION
# ========================================

"""
Core Backend Main Application - Wellness Companion AI
FastAPI application with comprehensive error handling and basic CORS
"""

import sys
import os

# Add project root to Python path for absolute imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from datetime import datetime
import logging

# Import error handling middleware with absolute imports
from src.api.middleware.error_handler import setup_error_handling

# Import routers with absolute imports
from src.api.endpoints.system.health import router as health_router
from src.api.endpoints.search.hybrid_search import router as search_router
from src.api.endpoints.search.semantic_search import router as semantic_search_router
from src.api.endpoints.search.web_search import router as web_search_router

# IMPORT ALL DOCUMENT ROUTERS
try:
    from src.api.endpoints.documents.upload import router as document_upload_router
    from src.api.endpoints.documents.list import router as document_list_router
    from src.api.endpoints.documents.details import router as document_details_router
    from src.api.endpoints.documents.delete import router as document_delete_router
    DOCUMENT_ROUTER_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("✅ All document routers imported successfully")
except Exception as e:
    DOCUMENT_ROUTER_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.error(f"❌ Document router failed: {e}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application with enhanced documentation
app = FastAPI(
    title="Wellness Companion AI - Core Backend API",
    description="""
# Wellness Companion AI - Core Backend API

## Overview

The **Wellness Companion AI Core Backend** is a sophisticated API service that provides document management, 
semantic search, web search integration, and AI-powered content analysis capabilities.

## Key Features

### 🗄️ Document Management
- **Upload & Processing**: Support for PDF, DOCX, TXT, MD, HTML, and RTF files
- **Metadata Extraction**: Automatic extraction of document metadata and content analysis
- **Version Control**: Document versioning and history tracking
- **Security**: User-based access control and document isolation

### 🔍 Advanced Search Capabilities
- **Semantic Search**: Vector-based similarity search using state-of-the-art embeddings
- **Web Search Integration**: Fallback to web search when local results have low confidence
- **Hybrid Search**: Intelligent combination of local and web search results
- **Real-time Results**: Fast, sub-second search responses

### 🤖 AI/ML Integration
- **Local LLM Processing**: Privacy-first AI processing using local language models
- **Embedding Generation**: High-quality document embeddings for semantic search
- **Content Analysis**: Automatic categorization, keyword extraction, and sentiment analysis

### 🔒 Security & Authentication
- **JWT Authentication**: Secure token-based authentication
- **OAuth Integration**: Support for Google OAuth and AWS Cognito
- **Rate Limiting**: Protection against abuse with configurable rate limits
- **Input Validation**: Comprehensive request validation and sanitization

### 🌐 CORS & Desktop Integration
- **Desktop App Support**: Full CORS support for PyQt6 desktop application
- **Security Headers**: Comprehensive security headers for production deployment
- **Cross-Origin**: Proper CORS configuration for web and desktop access

## Getting Started

1. **Authentication**: Obtain an access token using the `/api/auth/login` endpoint
2. **Document Upload**: Upload documents using the `/api/documents/upload` endpoint
3. **Search**: Perform searches using `/api/search/semantic`, `/api/search/web`, or `/api/search/hybrid`
4. **Document Management**: List, view, and manage documents using the document endpoints
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "system",
            "description": "System health monitoring and status endpoints"
        },
        {
            "name": "documents", 
            "description": "Document management - upload, list, view, delete documents"
        },
        {
            "name": "search",
            "description": "Advanced search capabilities - semantic, web, and hybrid search"
        },
        {
            "name": "authentication",
            "description": "User authentication and authorization (Phase 6)"
        }
    ]
)

# Add compression middleware first
app.add_middleware(GZipMiddleware, minimum_size=1000)

# SETUP ERROR HANDLING MIDDLEWARE FIRST (before other middleware)
debug_mode = os.getenv("DEBUG", "true").lower() == "true"
setup_error_handling(app, debug=debug_mode)

# SETUP BASIC CORS MIDDLEWARE - WORKING VERSION
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "app://localhost",
        "file://",
        "*"  # Allow all in development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
    allow_headers=[
        "Accept",
        "Accept-Language", 
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "X-Request-ID",
        "Origin",
        "Cache-Control",
        "X-API-Key",
        "*"  # Allow all headers
    ],
    expose_headers=["X-Request-ID", "X-Processing-Time", "X-Rate-Limit-Remaining"]
)

cors_type = "basic"

# Global variables for service status
SERVICE_STATUS = {
    "status": "starting",
    "started_at": datetime.utcnow().isoformat(),
    "version": "1.0.0",
    "environment": os.getenv("ENVIRONMENT", "development")
}

@app.on_event("startup")
async def startup_event():
    """Initialize service on startup"""
    logger.info("🚀 Starting Core Backend Service...")
    SERVICE_STATUS["status"] = "healthy"
    SERVICE_STATUS["ready_at"] = datetime.utcnow().isoformat()
    logger.info("✅ Core Backend Service started successfully")
    logger.info("🛡️ Global error handling middleware active")
    logger.info(f"🌐 CORS middleware active ({cors_type})")
    logger.info("📚 Enhanced API documentation available at /docs")

@app.on_event("shutdown")  
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🔄 Shutting down Core Backend Service...")
    SERVICE_STATUS["status"] = "shutting_down"

@app.get("/", tags=["system"])
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Wellness Companion AI - Core Backend",
        "status": "running",
        "message": "Welcome to the Core Backend API",
        "documentation": "/docs",
        "health_check": "/health",
        "api_status": "/api/status",
        "error_handling": "enabled",
        "cors_support": cors_type,
        "version": SERVICE_STATUS["version"],
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/ping", tags=["system"])
async def ping():
    """Simple ping endpoint for basic connectivity testing"""
    return {
        "message": "pong", 
        "timestamp": datetime.utcnow().isoformat(),
        "service": "core-backend",
        "cors_type": cors_type
    }

@app.get("/health", tags=["system"])
async def health_check():
    """
    Service health check endpoint
    
    Returns the current health status of the service and its dependencies.
    Used by load balancers and monitoring systems.
    """
    return {
        "status": SERVICE_STATUS["status"],
        "timestamp": datetime.utcnow().isoformat(),
        "service": "core-backend",
        "version": SERVICE_STATUS["version"],
        "uptime_started": SERVICE_STATUS["started_at"],
        "error_handling": "active",
        "cors_type": cors_type,
        "middleware": {
            "error_handling": "active",
            "cors": cors_type,
            "compression": "active",
            "validation": "active"
        }
    }

# OPTIONS handlers for CORS preflight
@app.options("/api/status", tags=["system"])
async def preflight_status():
    """Handle CORS preflight for status endpoint"""
    return Response(status_code=200)

@app.options("/api/{path:path}", tags=["system"])
async def preflight_all(path: str):
    """Handle CORS preflight for all API endpoints"""
    return Response(status_code=200)

@app.options("/", tags=["system"])
async def preflight_root():
    """Handle CORS preflight for root endpoint"""
    return Response(status_code=200)

@app.get("/api/status", tags=["system"])
async def get_status():
    """
    Comprehensive service status and capabilities
    
    Returns detailed information about service capabilities, 
    environment configuration, and feature availability.
    """
    capabilities = [
        "health_monitoring", 
        "service_discovery", 
        "api_gateway",
        "web_search",
        "error_handling",
        "request_validation",
        "api_documentation",
        "cors_support",
        "desktop_app_support"
    ]
    
    if DOCUMENT_ROUTER_AVAILABLE:
        capabilities.extend([
            "document_management", 
            "document_upload", 
            "document_listing", 
            "document_details",
            "semantic_search"
        ])
    
    return {
        "service_info": SERVICE_STATUS,
        "environment": {
            "aiml_service_url": os.getenv("AIML_SERVICE_URL", "http://aiml-orchestration:8000"),
            "data_layer_url": os.getenv("DATA_LAYER_URL", "http://data-layer:8000"),
            "redis_configured": bool(os.getenv("REDIS_URL")),
            "debug_mode": debug_mode,
        },
        "capabilities": capabilities,
        "features": {
            "document_router_available": DOCUMENT_ROUTER_AVAILABLE,
            "web_search_available": True,
            "error_handling_active": True,
            "api_documentation_active": True,
            "request_validation_active": True,
            "cors_support_active": True,
            "enhanced_cors_available": False,
            "desktop_app_ready": True
        },
        "middleware": {
            "error_handling": "active",
            "cors": cors_type,
            "compression": "active",
            "validation": "active"
        },
        "cors_info": {
            "type": cors_type,
            "desktop_origins_supported": True,
            "development_mode": debug_mode,
            "enhanced_available": False
        },
        "api_info": {
            "docs_url": "/docs",
            "redoc_url": "/redoc", 
            "openapi_url": "/openapi.json"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

# Include routers with proper tags
app.include_router(health_router, prefix="/api/system", tags=["system"])
app.include_router(search_router, prefix="/api/search", tags=["search"])

# REGISTER ALL DOCUMENT ROUTERS
if DOCUMENT_ROUTER_AVAILABLE:
    app.include_router(document_upload_router, prefix="/api/documents", tags=["documents"])
    app.include_router(document_list_router, prefix="/api/documents", tags=["documents"])
    app.include_router(document_details_router, prefix="/api/documents", tags=["documents"])
    app.include_router(document_delete_router, prefix="/api/documents", tags=["documents"])  
    app.include_router(semantic_search_router, prefix="/api/search", tags=["search"])
    logger.info("✅ All document routers registered successfully")
else:
    logger.warning("⚠️ Document routers not available")

# REGISTER WEB SEARCH ROUTER
app.include_router(web_search_router, prefix="/api/search", tags=["search"])
logger.info("✅ Web search router registered successfully")

# Test error handling endpoints (development only)
if debug_mode:
    @app.get("/api/test/error/{error_type}", tags=["system"], include_in_schema=False)
    async def test_error_handling(error_type: str):
        """Test error handling middleware - DEVELOPMENT ONLY"""
        
        if error_type == "500":
            raise Exception("Test 500 error - simulated internal server error")
        elif error_type == "validation":
            from pydantic import BaseModel, ValidationError
            try:
                class TestModel(BaseModel):
                    required_field: str
                TestModel(required_field=None)
            except ValidationError as e:
                raise e
        elif error_type == "custom":
            from src.core.exceptions import DocumentNotFoundError
            raise DocumentNotFoundError("test_doc_123")
        elif error_type == "timeout":
            import asyncio
            await asyncio.sleep(10)
        elif error_type == "not_found":
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Test 404 error")
        else:
            return {
                "message": f"Unknown error type: {error_type}",
                "available_types": ["500", "validation", "custom", "timeout", "not_found"],
                "description": "Use one of the available error types to test error handling"
            }

    @app.get("/api/test/cors", tags=["system"], include_in_schema=False)
    async def test_cors():
        """Test CORS configuration - DEVELOPMENT ONLY"""
        return {
            "message": "CORS test endpoint",
            "timestamp": datetime.utcnow().isoformat(),
            "cors_type": cors_type,
            "enhanced_cors_available": False,
            "headers_note": "Check response headers for CORS configuration"
        }

# Add custom OpenAPI configuration
def custom_openapi():
    """Custom OpenAPI schema with enhanced documentation"""
    if app.openapi_schema:
        return app.openapi_schema
    
    from fastapi.openapi.utils import get_openapi
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add enhanced metadata
    openapi_schema["info"]["contact"] = {
        "name": "Wellness Companion AI Team",
        "email": "api-support@wellness-companion.ai"
    }
    
    openapi_schema["info"]["license"] = {
        "name": "Proprietary"
    }
    
    # Add servers
    openapi_schema["servers"] = [
        {
            "url": "http://localhost:8001",
            "description": "Development server"
        },
        {
            "url": "https://api.wellness-companion.ai", 
            "description": "Production server"
        }
    ]
    
    # Cache the schema
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Set custom OpenAPI function
app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)