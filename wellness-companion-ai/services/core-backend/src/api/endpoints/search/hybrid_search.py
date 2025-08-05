"""RAG Query API - Hybrid Search Endpoint"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import httpx
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

class HybridSearchRequest(BaseModel):
    query: str
    max_results: int = 5
    confidence_threshold: float = 0.7
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None

class HybridSearchResponse(BaseModel):
    query: str
    results: List[Dict[str, Any]]
    sources: List[str]
    confidence: float
    search_type: str
    timestamp: str
    processing_time_ms: float

@router.post("/hybrid", response_model=HybridSearchResponse)
async def hybrid_search(request: HybridSearchRequest):
    """
    Perform hybrid search (local + web fallback)
    Connects to Phase 3 AI/ML orchestration service
    """
    start_time = datetime.utcnow()
    
    try:
        logger.info(f"Processing hybrid search query: {request.query[:50]}...")
        
        # Prepare request for AI/ML service
        aiml_request = {
            "query": request.query,
            "max_results": request.max_results,
            "confidence_threshold": request.confidence_threshold,
            "timestamp": start_time.isoformat()
        }
        
        if request.user_id:
            aiml_request["user_id"] = request.user_id
        if request.conversation_id:
            aiml_request["conversation_id"] = request.conversation_id
        
        # Call AI/ML orchestration service
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://aiml-orchestration:8000/search/hybrid",
                json=aiml_request
            )
            
            if response.status_code == 200:
                data = response.json()
                processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                
                # Format response
                formatted_response = HybridSearchResponse(
                    query=request.query,
                    results=data.get("results", []),
                    sources=data.get("sources", []),
                    confidence=data.get("confidence", 0.0),
                    search_type=data.get("search_type", "hybrid"),
                    timestamp=datetime.utcnow().isoformat(),
                    processing_time_ms=round(processing_time, 2)
                )
                
                logger.info(f"Hybrid search completed successfully: {len(formatted_response.results)} results")
                return formatted_response
                
            else:
                logger.error(f"AI/ML service error: {response.status_code}")
                raise HTTPException(
                    status_code=502,
                    detail=f"AI/ML service error: {response.status_code}"
                )
                
    except httpx.TimeoutException:
        logger.error("AI/ML service timeout")
        raise HTTPException(
            status_code=504,
            detail="Search service timeout"
        )
    except httpx.ConnectError:
        logger.error("Cannot connect to AI/ML service")
        raise HTTPException(
            status_code=503,
            detail="Search service unavailable"
        )
    except Exception as e:
        logger.error(f"Hybrid search failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal search error"
        )

@router.get("/test")
async def test_search_connection():
    """Test endpoint to verify AI/ML service connectivity"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://aiml-orchestration:8000/health")
            return {
                "aiml_service_status": response.status_code,
                "message": "AI/ML service reachable" if response.status_code == 200 else "AI/ML service issues",
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        return {
            "aiml_service_status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }