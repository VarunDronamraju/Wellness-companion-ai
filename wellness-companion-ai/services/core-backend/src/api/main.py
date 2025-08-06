# ========================================
# services/core-backend/src/api/main.py - UPDATED WITH ERROR HANDLING
# ========================================

"""
Core Backend Main Application - Wellness Companion AI
FastAPI application with comprehensive error handling middleware
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import logging
import os

# Import error handling middleware
from .middleware import setup_error_handling

# Import the health router
from .endpoints.system.health import router as health_router
from .endpoints.search.hybrid_search import router as search_router
from .endpoints.search.semantic_search import router as semantic_search_router
from .endpoints.search.web_search import router as web_search_router

# IMPORT ALL DOCUMENT ROUTERS
try:
    from .endpoints.documents.upload import router as document_upload_router
    from .endpoints.documents.list import router as document_list_router
    from .endpoints.documents.details import router as document_details_router
    from .endpoints.documents.delete import router as document_delete_router
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

# Create FastAPI application
app = FastAPI(
    title="Wellness Companion AI - Core Backend",
    description="Core Backend Service for API gateway, authentication, and service orchestration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# SETUP ERROR HANDLING MIDDLEWARE FIRST (before other middleware)
debug_mode = os.getenv("DEBUG", "true").lower() == "true"
setup_error_handling(app, debug=debug_mode)

# CORS middleware (after error handling)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.on_event("shutdown")  
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🔄 Shutting down Core Backend Service...")
    SERVICE_STATUS["status"] = "shutting_down"

@app.get("/")
async def root():
    return {
        "service": "Core Backend Service",
        "status": "running",
        "message": "Wellness Companion AI - Core Backend",
        "error_handling": "enabled",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/ping")
async def ping():
    return {"message": "pong", "timestamp": datetime.utcnow().isoformat()}

@app.get("/health")
async def health_check():
    return {
        "status": SERVICE_STATUS["status"],
        "timestamp": datetime.utcnow().isoformat(),
        "service": "core-backend",
        "version": SERVICE_STATUS["version"],
        "uptime_started": SERVICE_STATUS["started_at"],
        "error_handling": "active"
    }

@app.get("/api/status")
async def get_status():
    capabilities = [
        "health_monitoring", 
        "service_discovery", 
        "api_gateway",
        "web_search",
        "error_handling",  # NEW CAPABILITY
        "request_validation"  # NEW CAPABILITY
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
        "document_router_available": DOCUMENT_ROUTER_AVAILABLE,
        "web_search_available": True,
        "error_handling_active": True,  # NEW
        "middleware": {
            "error_handling": "active",
            "cors": "active",
            "validation": "active"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

# Include routers
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
    @app.get("/api/test/error/{error_type}")
    async def test_error_handling(error_type: str):
        """Test error handling middleware - DEVELOPMENT ONLY"""
        
        if error_type == "500":
            raise Exception("Test 500 error")
        elif error_type == "validation":
            from pydantic import ValidationError
            raise ValidationError("Test validation error", model=None)
        elif error_type == "custom":
            from ..core.exceptions import DocumentNotFoundError
            raise DocumentNotFoundError("test_doc_123")
        elif error_type == "timeout":
            import asyncio
            await asyncio.sleep(10)  # This will likely timeout
        else:
            return {"message": f"Unknown error type: {error_type}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)