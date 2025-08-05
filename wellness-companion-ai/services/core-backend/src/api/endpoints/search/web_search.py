# ========================================
# services/core-backend/src/api/endpoints/search/web_search.py
# ========================================

"""
Web Search API - POST /api/search/web
Web-only search endpoint using Tavily API
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from .web_search_handler import WebSearchHandler

logger = logging.getLogger(__name__)
router = APIRouter()

class WebSearchRequest(BaseModel):
    """Web search request model"""
    query: str = Field(..., description="Search query", min_length=2, max_length=500)
    max_results: int = Field(10, description="Maximum number of results", ge=1, le=20)
    search_depth: str = Field("basic", description="Search depth (basic/advanced)")
    user_id: str = Field(..., description="User ID for analytics and rate limiting")
    include_domains: Optional[List[str]] = Field(None, description="Domains to include in search")
    exclude_domains: Optional[List[str]] = Field(None, description="Domains to exclude from search")
    search_type: str = Field("web_only", description="Search type identifier")

class WebSearchResult(BaseModel):
    """Individual web search result"""
    title: str
    url: str
    snippet: str
    domain: str
    score: float
    published_date: Optional[str] = None

class WebSearchResponse(BaseModel):
    """Web search response model"""
    query: str
    results: List[WebSearchResult]
    total_results: int
    search_time_ms: float
    search_depth: str
    search_type: str = "web_only"
    source: str = "tavily_api"
    timestamp: str

@router.post("/web", response_model=WebSearchResponse)
async def web_search(request: WebSearchRequest):
    """Perform web search using Tavily API"""
    
    start_time = datetime.utcnow()
    logger.info(f"Web search request: '{request.query[:50]}...' by user {request.user_id}")
    
    try:
        # Initialize web search handler
        search_handler = WebSearchHandler()
        
        # Validate search parameters
        validated_params = await search_handler.validate_search_params({
            "query": request.query,
            "max_results": request.max_results,
            "search_depth": request.search_depth,
            "user_id": request.user_id
        })
        
        # Perform web search
        search_results = await search_handler.perform_web_search(
            query=validated_params["query"],
            max_results=validated_params["max_results"],
            search_depth=validated_params["search_depth"],
            user_id=validated_params["user_id"]
        )
        
        # Check for search errors
        if "error" in search_results:
            raise HTTPException(
                status_code=500,
                detail=f"Web search failed: {search_results['error']}"
            )
        
        # Format response
        formatted_results = []
        for result in search_results["results"]:
            formatted_results.append(WebSearchResult(
                title=result["title"],
                url=result["url"],
                snippet=result["snippet"],
                domain=result["domain"],
                score=result["score"],
                published_date=result.get("published_date")
            ))
        
        logger.info(f"Web search completed: {len(formatted_results)} results in {search_results['search_time_ms']:.2f}ms")
        
        return WebSearchResponse(
            query=search_results["query"],
            results=formatted_results,
            total_results=search_results["total_results"],
            search_time_ms=search_results["search_time_ms"],
            search_depth=search_results["search_depth"],
            timestamp=search_results["timestamp"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Web search endpoint failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Web search failed: {str(e)}"
        )

@router.get("/web/stats")
async def get_web_search_stats(user_id: str = Query(..., description="User ID")):
    """Get web search statistics for user"""
    
    try:
        search_handler = WebSearchHandler()
        stats = await search_handler.get_search_stats(user_id)
        
        return {
            "user_id": user_id,
            "web_search_stats": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get web search stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/web/health")
async def web_search_health():
    """Web search service health check"""
    
    try:
        # Test handler initialization
        search_handler = WebSearchHandler()
        
        # Perform a simple test search
        test_result = await search_handler.perform_web_search(
            query="test",
            max_results=1,
            user_id="health_check"
        )
        
        is_healthy = len(test_result.get("results", [])) >= 0  # Even 0 results is OK for health
        
        return {
            "service": "web_search",
            "status": "healthy" if is_healthy else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "test_search_time_ms": test_result.get("search_time_ms", 0.0)
        }
        
    except Exception as e:
        logger.error(f"Web search health check failed: {e}")
        return {
            "service": "web_search",
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }