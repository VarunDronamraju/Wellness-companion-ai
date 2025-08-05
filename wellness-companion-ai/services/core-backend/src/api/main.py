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
    allow_origins=["*"],  # Will be configured properly later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the health router
app.include_router(health_router, prefix="/api/system", tags=["system"])

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
    
    # Update service status
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
    """Root endpoint"""
    return {
        "service": "Core Backend Service",
        "status": "running",
        "message": "Wellness Companion AI - Core Backend",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/ping")
async def ping():
    """Simple ping endpoint"""
    return {"message": "pong", "timestamp": datetime.utcnow().isoformat()}

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker and monitoring"""
    
    # Basic health checks
    health_status = {
        "status": SERVICE_STATUS["status"],
        "timestamp": datetime.utcnow().isoformat(),
        "service": "core-backend",
        "version": SERVICE_STATUS["version"],
        "uptime_started": SERVICE_STATUS["started_at"]
    }
    
    return health_status

@app.get("/api/status")
async def get_status():
    """Detailed status endpoint"""
    return {
        "service_info": SERVICE_STATUS,
        "environment": {
            "aiml_service_url": os.getenv("AIML_SERVICE_URL", "http://aiml-orchestration:8000"),
            "data_layer_url": os.getenv("DATA_LAYER_URL", "http://data-layer:8000"),
            "redis_configured": bool(os.getenv("REDIS_URL")),
        },
        "capabilities": [
            "health_monitoring",
            "service_discovery",
            "api_gateway"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )