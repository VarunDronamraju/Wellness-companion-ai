"""
AI/ML Service Client - Wellness Companion AI
HTTP client for communicating with AI/ML Orchestration service
"""

from typing import Dict, Any, List, Optional, Union
import logging
from datetime import datetime

from .base_client import BaseHTTPClient
from .client_config import get_aiml_config, AIMLServiceConfig
from .exceptions import AIMLServiceException

logger = logging.getLogger(__name__)


class AIMLServiceClient(BaseHTTPClient):
    """Client for AI/ML Orchestration service"""
    
    def __init__(self):
        super().__init__(service_name="aiml-orchestration")
        self.config: AIMLServiceConfig = get_aiml_config()
        logger.info(f"Initialized AI/ML service client for {self.config.base_url}")
    
    # === HEALTH AND STATUS ===
    
    async def check_health(self) -> Dict[str, Any]:
        """Check AI/ML service health"""
        try:
            endpoint = self.config.get_endpoint("health")
            result = await self.get(endpoint)
            
            logger.debug("AI/ML service health check successful")
            return {
                "status": "healthy",
                "service": "aiml-orchestration",
                "timestamp": datetime.utcnow().isoformat(),
                "details": result
            }
            
        except Exception as e:
            logger.error(f"AI/ML service health check failed: {e}")
            raise AIMLServiceException(
                message=f"Health check failed: {str(e)}",
                operation="health_check"
            )
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get detailed AI/ML service status"""
        try:
            endpoint = self.config.get_endpoint("status")
            result = await self.get(endpoint)
            
            logger.debug("AI/ML service status retrieved successfully")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get AI/ML service status: {e}")
            raise AIMLServiceException(
                message=f"Status retrieval failed: {str(e)}",
                operation="get_status"
            )
    
    # === SEARCH OPERATIONS (Phase 3 Integration) ===
    
    async def hybrid_search(
        self,
        query: str,
        max_results: int = 5,
        confidence_threshold: float = 0.7,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Perform hybrid search (local + web fallback)"""
        try:
            endpoint = self.config.get_endpoint("hybrid_search")
            
            request_data = {
                "query": query,
                "max_results": max_results,
                "confidence_threshold": confidence_threshold,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add optional parameters
            if user_id:
                request_data["user_id"] = user_id
            if conversation_id:
                request_data["conversation_id"] = conversation_id
            
            logger.info(f"Performing hybrid search for query: '{query[:50]}...'")
            result = await self.post(endpoint, json_data=request_data)
            
            logger.info(
                f"Hybrid search completed - "
                f"Results: {len(result.get('results', []))}, "
                f"Confidence: {result.get('confidence', 'N/A')}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Hybrid search failed for query '{query}': {e}")
            raise AIMLServiceException(
                message=f"Hybrid search failed: {str(e)}",
                operation="hybrid_search"
            )
    
    async def semantic_search(
        self,
        query: str,
        max_results: int = 10,
        threshold: float = 0.7,
        document_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Perform semantic search (local only)"""
        try:
            endpoint = self.config.get_endpoint("semantic_search")
            
            request_data = {
                "query": query,
                "max_results": max_results,
                "threshold": threshold,
                "search_type": "semantic_only"
            }
            
            if document_ids:
                request_data["document_ids"] = document_ids
            
            logger.info(f"Performing semantic search for query: '{query[:50]}...'")
            result = await self.post(endpoint, json_data=request_data)
            
            logger.debug(f"Semantic search returned {len(result.get('results', []))} results")
            return result
            
        except Exception as e:
            logger.error(f"Semantic search failed for query '{query}': {e}")
            raise AIMLServiceException(
                message=f"Semantic search failed: {str(e)}",
                operation="semantic_search"
            )
    
    async def web_search(
        self,
        query: str,
        max_results: int = 5,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Perform web search (external only)"""
        try:
            endpoint = self.config.get_endpoint("web_search")
            
            request_data = {
                "query": query,
                "max_results": max_results,
                "search_type": "web_only"
            }
            
            if include_domains:
                request_data["include_domains"] = include_domains
            if exclude_domains:
                request_data["exclude_domains"] = exclude_domains
            
            logger.info(f"Performing web search for query: '{query[:50]}...'")
            result = await self.post(endpoint, json_data=request_data)
            
            logger.debug(f"Web search returned {len(result.get('results', []))} results")
            return result
            
        except Exception as e:
            logger.error(f"Web search failed for query '{query}': {e}")
            raise AIMLServiceException(
                message=f"Web search failed: {str(e)}",
                operation="web_search"
            )
    
    # === DOCUMENT OPERATIONS ===
    
    async def process_document(
        self,
        document_id: str,
        file_path: str,
        user_id: str,
        processing_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process document for embedding and indexing"""
        try:
            endpoint = self.config.get_endpoint("process_document")
            
            request_data = {
                "document_id": document_id,
                "file_path": file_path,
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if processing_options:
                request_data["options"] = processing_options
            
            logger.info(f"Requesting document processing for document: {document_id}")
            result = await self.post(endpoint, json_data=request_data)
            
            logger.info(f"Document processing initiated for {document_id}")
            return result
            
        except Exception as e:
            logger.error(f"Document processing failed for {document_id}: {e}")
            raise AIMLServiceException(
                message=f"Document processing failed: {str(e)}",
                operation="process_document"
            )
    
    async def get_document_status(self, document_id: str) -> Dict[str, Any]:
        """Get document processing status"""
        try:
            endpoint = self.config.get_endpoint("document_status")
            path_params = {"document_id": document_id}
            
            result = await self.get(endpoint, path_params=path_params)
            
            logger.debug(f"Retrieved status for document: {document_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get status for document {document_id}: {e}")
            raise AIMLServiceException(
                message=f"Document status retrieval failed: {str(e)}",
                operation="get_document_status"
            )
    
    # === VECTOR OPERATIONS ===
    
    async def vector_search(
        self,
        query_vector: List[float],
        collection_name: str = "documents",
        top_k: int = 10,
        score_threshold: float = 0.7
    ) -> Dict[str, Any]:
        """Perform vector similarity search"""
        try:
            endpoint = self.config.get_endpoint("vector_search")
            
            request_data = {
                "query_vector": query_vector,
                "collection_name": collection_name,
                "top_k": top_k,
                "score_threshold": score_threshold
            }
            
            logger.debug(f"Performing vector search in collection: {collection_name}")
            result = await self.post(endpoint, json_data=request_data)
            
            logger.debug(f"Vector search returned {len(result.get('matches', []))} matches")
            return result
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            raise AIMLServiceException(
                message=f"Vector search failed: {str(e)}",
                operation="vector_search"
            )
    
    async def store_vectors(
        self,
        vectors: List[Dict[str, Any]],
        collection_name: str = "documents"
    ) -> Dict[str, Any]:
        """Store vectors in the vector database"""
        try:
            endpoint = self.config.get_endpoint("vector_store")
            
            request_data = {
                "vectors": vectors,
                "collection_name": collection_name,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Storing {len(vectors)} vectors in collection: {collection_name}")
            result = await self.post(endpoint, json_data=request_data)
            
            logger.info(f"Successfully stored vectors in {collection_name}")
            return result
            
        except Exception as e:
            logger.error(f"Vector storage failed: {e}")
            raise AIMLServiceException(
                message=f"Vector storage failed: {str(e)}",
                operation="store_vectors"
            )
    
    # === UTILITY METHODS ===
    
    async def validate_connection(self) -> bool:
        """Validate connection to AI/ML service"""
        try:
            await self.check_health()
            return True
        except Exception as e:
            logger.warning(f"AI/ML service connection validation failed: {e}")
            return False
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service configuration information"""
        return {
            "service_name": self.service_name,
            "base_url": self.config.base_url,
            "endpoints": list(self.config.get_all_endpoints().keys()),
            "session_stats": self.get_session_stats()
        }


# === CLIENT FACTORY ===

_aiml_client_instance: Optional[AIMLServiceClient] = None


async def get_aiml_client() -> AIMLServiceClient:
    """Get AI/ML service client instance (singleton pattern)"""
    global _aiml_client_instance
    
    if _aiml_client_instance is None:
        _aiml_client_instance = AIMLServiceClient()
    
    return _aiml_client_instance


async def close_aiml_client():
    """Close AI/ML service client"""
    global _aiml_client_instance
    
    if _aiml_client_instance:
        await _aiml_client_instance.close_session()
        _aiml_client_instance = None