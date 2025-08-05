
"""
Core Backend Main Application - Wellness Companion AI
FastAPI application instance and basic endpoints
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import logging
import os

# Import the health router
from .endpoints.system.health import router as health_router
from .endpoints.search.hybrid_search import router as search_router
from .endpoints.search.semantic_search import router as semantic_search_router
# IMPORT ALL DOCUMENT ROUTERS
try:
    from .endpoints.documents.upload import router as document_upload_router
    from .endpoints.documents.list import router as document_list_router
    from .endpoints.documents.details import router as document_details_router
    from .endpoints.documents.delete import router as document_delete_router  # NEW
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

# CORS middleware
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
        "uptime_started": SERVICE_STATUS["started_at"]
    }

@app.get("/api/status")
async def get_status():
    capabilities = ["health_monitoring", "service_discovery", "api_gateway"]
    if DOCUMENT_ROUTER_AVAILABLE:
        capabilities.extend(["document_management", "document_upload", "document_listing", "document_details"])  # UPDATED
    
    return {
        "service_info": SERVICE_STATUS,
        "environment": {
            "aiml_service_url": os.getenv("AIML_SERVICE_URL", "http://aiml-orchestration:8000"),
            "data_layer_url": os.getenv("DATA_LAYER_URL", "http://data-layer:8000"),
            "redis_configured": bool(os.getenv("REDIS_URL")),
        },
        "capabilities": capabilities,
        "document_router_available": DOCUMENT_ROUTER_AVAILABLE,
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)