"""
AI/ML Orchestration Service - Main Application
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
    title="Wellness Companion AI - AI/ML Service",
    description="AI/ML Orchestration Service for RAG pipeline, embeddings, and LLM operations",
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
    logger.info("Starting AI/ML Orchestration Service...")
    SERVICE_STATUS["status"] = "healthy"
    SERVICE_STATUS["ready_at"] = datetime.utcnow().isoformat()
    logger.info("AI/ML Orchestration Service started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down AI/ML Orchestration Service...")
    SERVICE_STATUS["status"] = "shutting_down"

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AI/ML Orchestration Service",
        "status": "running",
        "message": "Wellness Companion AI - AI/ML Service",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker and monitoring"""
    health_status = {
        "status": SERVICE_STATUS["status"],
        "timestamp": datetime.utcnow().isoformat(),
        "service": "aiml-orchestration",
        "version": SERVICE_STATUS["version"],
        "uptime_started": SERVICE_STATUS["started_at"]
    }
    
    if SERVICE_STATUS["status"] != "healthy":
        raise HTTPException(status_code=503, detail="Service not ready")
    
    return health_status

@app.get("/status")
async def get_status():
    """Detailed status endpoint"""
    return {
        "service_info": SERVICE_STATUS,
        "environment": {
            "ollama_url": os.getenv("OLLAMA_URL", "http://ollama:11434"),
            "qdrant_url": os.getenv("QDRANT_URL", "http://qdrant:6333"),
            "data_layer_url": os.getenv("DATA_LAYER_URL", "http://data-layer:8000"),
            "redis_configured": bool(os.getenv("REDIS_URL")),
            "tavily_configured": bool(os.getenv("TAVILY_API_KEY"))
        },
        "capabilities": [
            "health_monitoring",
            "service_discovery"
        ],
        "planned_features": [
            "rag_pipeline",
            "embedding_generation",
            "vector_search",
            "llm_integration",
            "web_search_fallback"
        ]
    }

@app.get("/ping")
async def ping():
    """Simple ping endpoint"""
    return {"message": "pong", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("ENVIRONMENT") == "development"
    )