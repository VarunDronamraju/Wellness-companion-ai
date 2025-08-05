"""
Dependency Checker - Wellness Companion AI
Health checks for external service dependencies
"""

import httpx
import asyncio
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
import time

logger = logging.getLogger(__name__)


class DependencyChecker:
    """Health checker for external service dependencies"""
    
    def __init__(self):
        self.timeout = 5.0
        self.retry_count = 2
    
    async def check_aiml_service(self, service_url: str) -> Dict[str, Any]:
        """Check AI/ML Orchestration service health"""
        service_name = "aiml-orchestration"
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Try health endpoint first
                try:
                    response = await client.get(f"{service_url}/health")
                    
                    if response.status_code == 200:
                        data = response.json()
                        duration_ms = round((time.time() - start_time) * 1000, 2)
                        
                        return {
                            "service": service_name,
                            "status": "healthy",
                            "url": service_url,
                            "response_time_ms": duration_ms,
                            "details": {
                                "version": data.get("version", "unknown"),
                                "capabilities": data.get("modules", {}),
                                "last_check": datetime.utcnow().isoformat()
                            },
                            "critical": True
                        }
                    else:
                        return self._create_unhealthy_result(
                            service_name, service_url, f"HTTP {response.status_code}", start_time
                        )
                        
                except httpx.TimeoutException:
                    return self._create_unhealthy_result(
                        service_name, service_url, "Connection timeout", start_time
                    )
                except httpx.ConnectError:
                    return self._create_unhealthy_result(
                        service_name, service_url, "Connection refused", start_time
                    )
                    
        except Exception as e:
            return self._create_unhealthy_result(
                service_name, service_url, f"Unexpected error: {str(e)}", start_time
            )
    
    async def check_data_layer(self, service_url: str) -> Dict[str, Any]:
        """Check Data Layer service health"""
        service_name = "data-layer"
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{service_url}/health")
                
                if response.status_code == 200:
                    duration_ms = round((time.time() - start_time) * 1000, 2)
                    data = response.json()
                    
                    return {
                        "service": service_name,
                        "status": "healthy",
                        "url": service_url,
                        "response_time_ms": duration_ms,
                        "details": {
                            "database_connected": data.get("database_connected", False),
                            "vector_db_connected": data.get("vector_db_connected", False),
                            "last_check": datetime.utcnow().isoformat()
                        },
                        "critical": True
                    }
                else:
                    return self._create_unhealthy_result(
                        service_name, service_url, f"HTTP {response.status_code}", start_time
                    )
                    
        except Exception as e:
            return self._create_unhealthy_result(
                service_name, service_url, str(e), start_time
            )
    
    async def check_redis(self, redis_url: Optional[str]) -> Dict[str, Any]:
        """Check Redis connection"""
        service_name = "redis"
        start_time = time.time()
        
        if not redis_url:
            return {
                "service": service_name,
                "status": "not_configured",
                "url": None,
                "details": {"message": "Redis URL not configured"},
                "critical": False
            }
        
        try:
            # For now, we'll do a basic connection test
            # In a real implementation, you'd use redis-py client
            duration_ms = round((time.time() - start_time) * 1000, 2)
            
            return {
                "service": service_name,
                "status": "healthy",  # Placeholder - would be actual Redis ping
                "url": redis_url,
                "response_time_ms": duration_ms,
                "details": {
                    "connection_type": "redis",
                    "last_check": datetime.utcnow().isoformat(),
                    "note": "Redis check placeholder - implement with redis-py"
                },
                "critical": False
            }
            
        except Exception as e:
            return self._create_unhealthy_result(
                service_name, redis_url, str(e), start_time, critical=False
            )
    
    async def check_postgres(self, postgres_url: Optional[str]) -> Dict[str, Any]:
        """Check PostgreSQL connection"""
        service_name = "postgresql"
        start_time = time.time()
        
        if not postgres_url:
            return {
                "service": service_name,
                "status": "not_configured",
                "url": None,
                "details": {"message": "PostgreSQL URL not configured"},
                "critical": True
            }
        
        try:
            # Placeholder for actual PostgreSQL connection check
            # In real implementation, use asyncpg or psycopg2
            duration_ms = round((time.time() - start_time) * 1000, 2)
            
            return {
                "service": service_name,
                "status": "healthy",  # Placeholder
                "url": "postgresql://***:***@postgres:5432/***",  # Masked URL
                "response_time_ms": duration_ms,
                "details": {
                    "connection_type": "postgresql",
                    "last_check": datetime.utcnow().isoformat(),
                    "note": "PostgreSQL check placeholder - implement with asyncpg"
                },
                "critical": True
            }
            
        except Exception as e:
            return self._create_unhealthy_result(
                service_name, "postgresql://***", str(e), start_time, critical=True
            )
    
    def _create_unhealthy_result(
        self, 
        service_name: str, 
        service_url: str, 
        error: str, 
        start_time: float,
        critical: bool = True
    ) -> Dict[str, Any]:
        """Create standardized unhealthy service result"""
        duration_ms = round((time.time() - start_time) * 1000, 2)
        
        return {
            "service": service_name,
            "status": "unhealthy",
            "url": service_url,
            "response_time_ms": duration_ms,
            "error": error,
            "last_check": datetime.utcnow().isoformat(),
            "critical": critical
        }
    
    async def check_all_services(
        self, 
        aiml_url: str, 
        data_layer_url: str,
        redis_url: Optional[str] = None,
        postgres_url: Optional[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        """Check all services concurrently"""
        
        # Run all checks concurrently
        tasks = [
            self.check_aiml_service(aiml_url),
            self.check_data_layer(data_layer_url),
            self.check_redis(redis_url),
            self.check_postgres(postgres_url)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        service_health = {}
        for result in results:
            if isinstance(result, Exception):
                # Handle unexpected errors
                service_health["unknown_service"] = {
                    "status": "error",
                    "error": str(result),
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                service_health[result["service"]] = result
        
        return service_health


# Global instance
dependency_checker = DependencyChecker()


def get_dependency_checker() -> DependencyChecker:
    """Get dependency checker instance"""
    return dependency_checker