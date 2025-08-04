# services/aiml-orchestration/src/main.py
"""
AI/ML Orchestration Service - Main Application
Wellness Companion AI
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import uvicorn
import os
from datetime import datetime
import logging
# TASK 31: Web Search Imports
from src.search.web_search import web_search_service, WebSearchResponse
from src.search.web_search_config import web_search_config
from src.search.tavily_client import TavilyAPIError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


from pydantic import BaseModel

# TASK 16: Import all modules (absolute imports) - COMMENTED FOR NOW
try:
    # Note: These imports will be populated as we progress through tasks
    # from src.orchestrators import rag_orchestrator
    # from src.search import vector_search
    # from src.llm import ollama_client
    # from src.embeddings import sentence_transformers
    # from src.reranking import neural_rerank
    # from src.pipelines import async_pipeline
    # from src.utils import cython_core
    
    # For now, just verify modules exist
    import sys
    import importlib.util
    
    # Check if module directories exist
    module_paths = {
        "orchestrators": "src/orchestrators",
        "search": "src/search", 
        "llm": "src/llm",
        "embeddings": "src/embeddings",
        "reranking": "src/reranking",
        "pipelines": "src/pipelines",
        "utils": "src/utils"
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
    "modules": modules_status
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
    
    # TASK 31: Initialize web search service
    if web_search_config.enable_web_search:
        logger.info("Web search service enabled")
    else:
        logger.warning("Web search service disabled")
    
    SERVICE_STATUS["status"] = "healthy"
    SERVICE_STATUS["ready_at"] = datetime.utcnow().isoformat()
    SERVICE_STATUS["modules"] = modules_status
    logger.info("AI/ML Orchestration Service started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down AI/ML Orchestration Service...")
    
    # TASK 31: Cleanup web search service
    await web_search_service.cleanup()
    
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
            "search": "Vector similarity search + Web search", 
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
        required_envs = ["OLLAMA_HOST", "QDRANT_HOST"]
        missing_envs = [env for env in required_envs if not os.getenv(env)]
        
        health_status = {
            "status": SERVICE_STATUS["status"],
            "timestamp": datetime.utcnow().isoformat(),
            "service": "aiml-orchestration",
            "version": SERVICE_STATUS["version"],
            "uptime_started": SERVICE_STATUS["started_at"],
            "modules_status": SERVICE_STATUS.get("modules", {}),
            "web_search_enabled": web_search_config.enable_web_search,
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
            "ollama_host": os.getenv("OLLAMA_HOST", "ollama"),
            "ollama_port": os.getenv("OLLAMA_PORT", "11434"),
            "qdrant_host": os.getenv("QDRANT_HOST", "qdrant"),
            "qdrant_port": os.getenv("QDRANT_PORT", "6333"),
            "data_layer_url": os.getenv("DATA_LAYER_URL", "http://data-layer:8002"),
            "redis_configured": bool(os.getenv("REDIS_HOST")),
            "tavily_configured": bool(os.getenv("TAVILY_API_KEY") and os.getenv("TAVILY_API_KEY") != "your_tavily_api_key_here")
        },
        "modules": {
            "orchestrators": {"status": modules_status.get("orchestrators", "unknown"), "description": "RAG orchestration ready"},
            "search": {"status": modules_status.get("search", "unknown"), "description": "Vector + Web search ready"}, 
            "llm": {"status": modules_status.get("llm", "unknown"), "description": "LLM integration ready"},
            "embeddings": {"status": modules_status.get("embeddings", "unknown"), "description": "Embedding service ready"},
            "reranking": {"status": modules_status.get("reranking", "unknown"), "description": "Reranking service ready"},
            "pipelines": {"status": modules_status.get("pipelines", "unknown"), "description": "Pipeline processing ready"},
            "utils": {"status": modules_status.get("utils", "unknown"), "description": "Utilities ready"}
        },
        "capabilities": [
            "health_monitoring",
            "service_discovery",
            "module_management",
            "web_search_integration"
        ],
        "planned_features": [
            "rag_pipeline",
            "embedding_generation", 
            "vector_search",
            "llm_integration",
            "web_search_fallback"
        ],
        "task_progress": {
            "task_16": "completed" if all(status == "initialized" for status in modules_status.values()) else "in_progress",
            "task_31": "completed",
            "next_task": "task_32_web_search_processing"
        }
    }

@app.get("/ping")
async def ping():
    """Simple ping endpoint"""
    return {"message": "pong", "timestamp": datetime.utcnow().isoformat()}

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


# ADD PYDANTIC MODELS
class SearchRequest(BaseModel):
    query: str
    max_results: int = 5
    search_depth: str = "basic"
    include_domains: Optional[List[str]] = None
    exclude_domains: Optional[List[str]] = None

class QuickSearchRequest(BaseModel):
    query: str
    max_results: int = 3

class NewsSearchRequest(BaseModel):
    query: str
    max_results: int = 5

# REPLACE ALL WEB SEARCH ENDPOINTS
@app.post("/api/web-search/search")
async def web_search_endpoint(request: SearchRequest):
    """Perform web search using Tavily API"""
    try:
        result = await web_search_service.search(
            query=request.query,
            max_results=request.max_results,
            search_depth=request.search_depth,
            include_domains=request.include_domains,
            exclude_domains=request.exclude_domains
        )
        
        if result is None:
            raise HTTPException(status_code=503, detail="Web search service unavailable")
        
        return result.to_dict()
    
    except Exception as e:
        logger.error(f"Web search endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/web-search/quick")
async def quick_web_search(request: QuickSearchRequest):
    """Quick web search with minimal results"""
    try:
        result = await web_search_service.quick_search(request.query, request.max_results)
        
        if result is None:
            raise HTTPException(status_code=503, detail="Web search service unavailable")
        
        return result.to_dict()
    
    except Exception as e:
        logger.error(f"Quick web search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/web-search/news")  
async def news_search(request: NewsSearchRequest):
    """Search for news articles"""
    try:
        result = await web_search_service.news_search(request.query, request.max_results)
        
        if result is None:
            raise HTTPException(status_code=503, detail="News search service unavailable")
        
        return result.to_dict()
    
    except Exception as e:
        logger.error(f"News search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/web-search/health")
async def web_search_health():
    """Check web search service health"""
    try:
        health_status = await web_search_service.health_check()
        return health_status
    
    except Exception as e:
        logger.error(f"Web search health check error: {str(e)}")
        return {"service_enabled": False, "error": str(e)}

@app.get("/api/web-search/suggestions")
async def get_search_suggestions(partial_query: str):
    """Get search suggestions"""
    try:
        suggestions = await web_search_service.get_search_suggestions(partial_query)
        return {"suggestions": suggestions}
    
    except Exception as e:
        logger.error(f"Search suggestions error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))