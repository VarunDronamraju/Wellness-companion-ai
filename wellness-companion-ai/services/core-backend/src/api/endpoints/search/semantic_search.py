# ========================================
# services/core-backend/src/api/endpoints/search/semantic_search.py - ABSOLUTE IMPORTS
# ========================================

"""
Semantic Search API - POST /api/search/semantic
Local-only vector search endpoint
"""

import sys
import os

# Add project root to Python path for absolute imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

# Use relative import for local handler (same directory)
from .local_search_handler import LocalSearchHandler

# Use absolute import for aiml_client
from src.integrations.aiml_client import get_aiml_client

logger = logging.getLogger(__name__)
router = APIRouter()

class SemanticSearchRequest(BaseModel):
    """Semantic search request model"""
    query: str = Field(..., description="Search query", min_length=1, max_length=500)
    max_results: int = Field(10, description="Maximum number of results", ge=1, le=100)
    threshold: float = Field(0.7, description="Similarity threshold", ge=0.0, le=1.0)
    document_ids: Optional[List[str]] = Field(None, description="Limit search to specific documents")
    user_id: str = Field(..., description="User ID for document access control")
    include_metadata: bool = Field(True, description="Include document metadata in results")
    search_type: str = Field("semantic_only", description="Search type identifier")

class SemanticSearchResult(BaseModel):
    """Individual search result"""
    document_id: str
    filename: str
    relevance_score: float
    content_snippet: str
    metadata: Optional[Dict[str, Any]] = None

class SemanticSearchResponse(BaseModel):
    """Semantic search response model"""
    query: str
    results: List[SemanticSearchResult]
    total_results: int
    search_time_ms: float
    threshold_used: float
    search_type: str = "semantic_only"
    timestamp: str

@router.post("/semantic", response_model=SemanticSearchResponse)
async def semantic_search(request: SemanticSearchRequest):
    """Perform semantic search using local vector database only"""
    
    start_time = datetime.utcnow()
    logger.info(f"Semantic search request: '{request.query[:50]}...' by user {request.user_id}")
    
    try:
        # Initialize local search handler
        search_handler = LocalSearchHandler()
        
        # Validate user has documents
        user_doc_count = await search_handler.get_user_document_count(request.user_id)
        if user_doc_count == 0:
            return SemanticSearchResponse(
                query=request.query,
                results=[],
                total_results=0,
                search_time_ms=0.0,
                threshold_used=request.threshold,
                timestamp=datetime.utcnow().isoformat()
            )
        
        # Get AI/ML client for vector search
        aiml_client = await get_aiml_client()
        
        # Perform semantic search
        search_params = {
            "query_text": request.query,
            "limit": request.max_results,
            "threshold": request.threshold,
            "user_id": request.user_id
        }
        
        if request.document_ids:
            search_params["document_ids"] = request.document_ids
        
        # Call AI/ML service for vector search
        vector_results = await aiml_client.semantic_search(**search_params)
        
        # Process results through local handler
        processed_results = await search_handler.process_search_results(
            vector_results,
            request.user_id,
            include_metadata=request.include_metadata
        )
        
        # Calculate search time
        end_time = datetime.utcnow()
        search_time_ms = (end_time - start_time).total_seconds() * 1000
        
        # Format response
        formatted_results = []
        for result in processed_results:
            formatted_results.append(SemanticSearchResult(
                document_id=result["document_id"],
                filename=result["filename"],
                relevance_score=result["score"],
                content_snippet=result["snippet"],
                metadata=result.get("metadata") if request.include_metadata else None
            ))
        
        logger.info(f"Semantic search completed: {len(formatted_results)} results in {search_time_ms:.2f}ms")
        
        return SemanticSearchResponse(
            query=request.query,
            results=formatted_results,
            total_results=len(formatted_results),
            search_time_ms=search_time_ms,
            threshold_used=request.threshold,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Semantic search failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Semantic search failed: {str(e)}"
        )

@router.get("/semantic/stats")
async def get_semantic_search_stats(user_id: str):
    """Get semantic search statistics for user"""
    
    try:
        search_handler = LocalSearchHandler()
        stats = await search_handler.get_search_stats(user_id)
        
        return {
            "user_id": user_id,
            "semantic_search_stats": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get semantic search stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))