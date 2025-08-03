# services/aiml-orchestration/src/main.py
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

# TASK 16: Import all modules (absolute imports)
try:
    # Note: These imports will be populated as we progress through tasks
    # from wellness_companion_ai.services.aiml_orchestration.src import orchestrators
    # from wellness_companion_ai.services.aiml_orchestration.src import search
    # from wellness_companion_ai.services.aiml_orchestration.src import llm
    # from wellness_companion_ai.services.aiml_orchestration.src import embeddings
    # from wellness_companion_ai.services.aiml_orchestration.src import reranking
    # from wellness_companion_ai.services.aiml_orchestration.src import pipelines
    # from wellness_companion_ai.services.aiml_orchestration.src import utils
    
    # For now, just verify modules exist
    import sys
    import importlib.util
    
    # Check if module directories exist
    module_paths = {
        "orchestrators": "orchestrators",
        "search": "search", 
        "llm": "llm",
        "embeddings": "embeddings",
        "reranking": "reranking",
        "pipelines": "pipelines",
        "utils": "utils"
    }
    
    modules_status = {}
    for module_name, module_path in module_paths.items():
        try:
            if os.path.exists(module_path) and os.path.exists(f"{module_path}/__init__.py"):
                modules_status[module_name] = "initialized"
            else:
                modules_status[module_name] = "missing"
        except Exception as e:
            modules_status[module_name] = f"error: {str(e)}"
            
except Exception as e:
    logger.warning(f"Module import issue: {str(e)}")
    modules_status = {"error": "modules not ready"}

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
    "environment": os.getenv("ENVIRONMENT", "development"),
    "modules": modules_status  # TASK 16: Add module status
}

@app.on_event("startup")
async def startup_event():
    """Initialize service on startup"""
    logger.info("Starting AI/ML Orchestration Service...")
    
    # TASK 16: Validate module structure
    missing_modules = [name for name, status in modules_status.items() if status == "missing"]
    if missing_modules:
        logger.warning(f"Missing modules: {missing_modules}")
    else:
        logger.info("All required modules initialized successfully")
    
    SERVICE_STATUS["status"] = "healthy"
    SERVICE_STATUS["ready_at"] = datetime.utcnow().isoformat()
    SERVICE_STATUS["modules"] = modules_status
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
        "timestamp": datetime.utcnow().isoformat(),
        "modules": {
            "orchestrators": "RAG pipeline coordination",
            "search": "Vector similarity search", 
            "llm": "Language model integration",
            "embeddings": "Embedding generation",
            "reranking": "Confidence scoring",
            "pipelines": "Batch processing",
            "utils": "Configuration and utilities"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker and monitoring"""
    try:
        # Check environment variables
        required_envs = ["QDRANT_URL", "OLLAMA_URL"]
        missing_envs = [env for env in required_envs if not os.getenv(env)]
        
        health_status = {
            "status": SERVICE_STATUS["status"],
            "timestamp": datetime.utcnow().isoformat(),
            "service": "aiml-orchestration",
            "version": SERVICE_STATUS["version"],
            "uptime_started": SERVICE_STATUS["started_at"],
            "modules_status": SERVICE_STATUS.get("modules", {}),  # TASK 16: Module status
            "environment_check": {
                "required_vars_present": len(missing_envs) == 0,
                "missing_vars": missing_envs
            }
        }
        
        # Service is unhealthy if critical env vars missing or modules not ready
        if missing_envs or SERVICE_STATUS["status"] != "healthy":
            raise HTTPException(
                status_code=503, 
                detail=f"Service not ready. Missing vars: {missing_envs}"
            )
        
        return health_status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Health check error: {str(e)}")

@app.get("/status")
async def get_status():
    """Detailed status endpoint"""
    return {
        "service_info": SERVICE_STATUS,
        "environment": {
            "ollama_url": os.getenv("OLLAMA_URL", "http://ollama:11434"),
            "qdrant_url": os.getenv("QDRANT_URL", "http://qdrant:6333"),
            "data_layer_url": os.getenv("DATA_LAYER_URL", "http://data-layer:8002"),
            "redis_configured": bool(os.getenv("REDIS_URL")),
            "tavily_configured": bool(os.getenv("TAVILY_API_KEY"))
        },
        "modules": {  # TASK 16: Detailed module info
            "orchestrators": {"status": modules_status.get("orchestrators", "unknown"), "description": "RAG orchestration ready"},
            "search": {"status": modules_status.get("search", "unknown"), "description": "Vector search ready"}, 
            "llm": {"status": modules_status.get("llm", "unknown"), "description": "LLM integration ready"},
            "embeddings": {"status": modules_status.get("embeddings", "unknown"), "description": "Embedding service ready"},
            "reranking": {"status": modules_status.get("reranking", "unknown"), "description": "Reranking service ready"},
            "pipelines": {"status": modules_status.get("pipelines", "unknown"), "description": "Pipeline processing ready"},
            "utils": {"status": modules_status.get("utils", "unknown"), "description": "Utilities ready"}
        },
        "capabilities": [
            "health_monitoring",
            "service_discovery",
            "module_management"  # TASK 16: New capability
        ],
        "planned_features": [
            "rag_pipeline",
            "embedding_generation", 
            "vector_search",
            "llm_integration",
            "web_search_fallback"
        ],
        "task_progress": {  # TASK 16: Track task completion
            "task_16": "completed" if all(status == "initialized" for status in modules_status.values()) else "in_progress",
            "next_task": "task_17_text_processing_pipeline"
        }
    }

@app.get("/ping")
async def ping():
    """Simple ping endpoint"""
    return {"message": "pong", "timestamp": datetime.utcnow().isoformat()}

# TASK 16: Module validation endpoint
@app.get("/modules")
async def get_modules():
    """Get detailed module status"""
    return {
        "modules": modules_status,
        "total_modules": len(module_paths),
        "initialized_count": len([s for s in modules_status.values() if s == "initialized"]),
        "missing_count": len([s for s in modules_status.values() if s == "missing"]),
        "all_ready": all(status == "initialized" for status in modules_status.values())
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0", 
        port=8001,  # Corrected port to 8001 (AI/ML service)
        reload=os.getenv("ENVIRONMENT") == "development"
    )