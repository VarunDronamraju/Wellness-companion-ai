"""
Core Backend Service - Main Application
Wellness Companion AI
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from datetime import datetime
import logging

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
    allow_origins=["*"],  # Configure properly in production
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
    
    # Check if service is healthy
    if SERVICE_STATUS["status"] != "healthy":
        raise HTTPException(status_code=503, detail="Service not ready")
    
    return health_status

@app.get("/status")
async def get_status():
    """Detailed status endpoint"""
    return {
        "service_info": SERVICE_STATUS,
        "environment": {
            "aiml_service_url": os.getenv("AIML_SERVICE_URL", "http://aiml-orchestration:8000"),
            "data_layer_url": os.getenv("DATA_LAYER_URL", "http://data-layer:8000"),
            "redis_configured": bool(os.getenv("REDIS_URL")),
            "jwt_configured": bool(os.getenv("JWT_SECRET_KEY")),
            "google_oauth_configured": bool(os.getenv("GOOGLE_CLIENT_ID")),
            "aws_cognito_configured": bool(os.getenv("AWS_COGNITO_USER_POOL_ID"))
        },
        "capabilities": [
            "health_monitoring",
            "service_discovery",
            "api_gateway"
        ],
        "planned_features": [
            "authentication",
            "document_management",
            "chat_management",
            "search_orchestration",
            "rate_limiting"
        ]
    }

@app.get("/ping")
async def ping():
    """Simple ping endpoint"""
    return {"message": "pong", "timestamp": datetime.utcnow().isoformat()}

# Placeholder endpoints for future implementation (Phase 2+)
@app.get("/api/auth/profile")
async def auth_profile():
    """User profile endpoint - Phase 6 implementation"""
    return {
        "message": "Authentication will be implemented in Phase 6",
        "planned_features": ["google_oauth", "aws_cognito", "jwt_tokens"],
        "status": "not_implemented"
    }

@app.get("/api/documents")
async def list_documents():
    """Document management endpoint - Phase 4 implementation"""
    return {
        "message": "Document management will be implemented in Phase 4",
        "planned_features": ["upload", "list", "delete", "metadata"],
        "status": "not_implemented"
    }

@app.get("/api/chat/conversations")
async def list_conversations():
    """Chat management endpoint - Phase 4 implementation"""
    return {
        "message": "Chat management will be implemented in Phase 4",
        "planned_features": ["conversations", "messages", "history"],
        "status": "not_implemented"
    }

@app.get("/api/search")
async def search_endpoint():
    """Search orchestration endpoint - Phase 2 implementation"""
    return {
        "message": "Search orchestration will be implemented in Phase 2",
        "planned_features": ["semantic_search", "hybrid_search", "web_fallback"],
        "status": "not_implemented"
    }

if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("ENVIRONMENT") == "development"
    )