"""
Client Configuration - Wellness Companion AI
Configuration for external service clients
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from ..core.settings import settings
import logging

logger = logging.getLogger(__name__)


@dataclass
class ServiceEndpoint:
    """Configuration for a service endpoint"""
    url: str
    timeout: int
    retries: int
    retry_delay: float
    
    def __post_init__(self):
        """Validate endpoint configuration"""
        if not self.url.startswith(('http://', 'https://')):
            raise ValueError(f"Invalid URL format: {self.url}")
        
        if self.timeout <= 0:
            raise ValueError(f"Timeout must be positive: {self.timeout}")
        
        if self.retries < 0:
            raise ValueError(f"Retries must be non-negative: {self.retries}")


class AIMLServiceConfig:
    """Configuration for AI/ML Orchestration service"""
    
    def __init__(self):
        self.base_url = settings.aiml_service_url.rstrip('/')
        self.service_name = "aiml-orchestration"
        
        # Endpoint configurations
        self.endpoints = {
            # Health and status
            "health": ServiceEndpoint(
                url=f"{self.base_url}/health",
                timeout=5,
                retries=2,
                retry_delay=1.0
            ),
            "status": ServiceEndpoint(
                url=f"{self.base_url}/status",
                timeout=10,
                retries=1,
                retry_delay=1.0
            ),
            
            # Search endpoints (Phase 3 integration)
            "hybrid_search": ServiceEndpoint(
                url=f"{self.base_url}/search/hybrid",
                timeout=30,
                retries=2,
                retry_delay=2.0
            ),
            "semantic_search": ServiceEndpoint(
                url=f"{self.base_url}/search/semantic",
                timeout=20,
                retries=2,
                retry_delay=1.5
            ),
            "web_search": ServiceEndpoint(
                url=f"{self.base_url}/search/web",
                timeout=15,
                retries=1,
                retry_delay=1.0
            ),
            
            # Document processing
            "process_document": ServiceEndpoint(
                url=f"{self.base_url}/documents/process",
                timeout=60,
                retries=1,
                retry_delay=3.0
            ),
            "document_status": ServiceEndpoint(
                url=f"{self.base_url}/documents/status",
                timeout=10,
                retries=2,
                retry_delay=1.0
            ),
            
            # Vector operations
            "vector_search": ServiceEndpoint(
                url=f"{self.base_url}/vector/search",
                timeout=25,
                retries=2,
                retry_delay=2.0
            ),
            "vector_store": ServiceEndpoint(
                url=f"{self.base_url}/vector/store",
                timeout=30,
                retries=1,
                retry_delay=2.0
            )
        }
        
        logger.info(f"AI/ML service configured: {self.base_url}")
    
    def get_endpoint(self, endpoint_name: str) -> ServiceEndpoint:
        """Get endpoint configuration by name"""
        if endpoint_name not in self.endpoints:
            raise ValueError(f"Unknown endpoint: {endpoint_name}")
        return self.endpoints[endpoint_name]
    
    def get_all_endpoints(self) -> Dict[str, ServiceEndpoint]:
        """Get all endpoint configurations"""
        return self.endpoints.copy()
    
    def validate_connectivity(self) -> bool:
        """Validate that the base URL is reachable"""
        try:
            import httpx
            with httpx.Client(timeout=5) as client:
                response = client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"AI/ML service connectivity check failed: {e}")
            return False


# Global configuration instances
aiml_config = AIMLServiceConfig()


def get_aiml_config() -> AIMLServiceConfig:
    """Get AI/ML service configuration"""
    return aiml_config


def validate_all_configs() -> Dict[str, bool]:
    """Validate all service configurations"""
    results = {
        "aiml_service": aiml_config.validate_connectivity()
    }
    
    logger.info(f"Service configuration validation: {results}")
    return results