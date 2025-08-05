"""
Health Service - Wellness Companion AI
Business logic for health checks and service monitoring
"""

from typing import Dict, Any, List, Optional
import logging
import asyncio
import time
from datetime import datetime

from ..api.endpoints.system.dependency_checker import get_dependency_checker, DependencyChecker
from ..core.settings import settings

logger = logging.getLogger(__name__)


class HealthService:
    """Service for managing health checks and monitoring"""
    
    def __init__(self):
        self.dependency_checker: DependencyChecker = get_dependency_checker()
        self.critical_services = ["aiml-orchestration", "data-layer"]
        self.optional_services = ["redis", "postgresql"]
    
    async def check_all_dependencies(self) -> Dict[str, Any]:
        """Check all service dependencies"""
        start_time = time.time()
        
        try:
            logger.info("Starting comprehensive health checks...")
            
            # Get service URLs from settings
            service_urls = {
                "aiml_url": settings.aiml_service_url,
                "data_layer_url": settings.data_layer_url,
                "redis_url": settings.redis_url,
                "postgres_url": getattr(settings, 'postgres_url', None)
            }
            
            # Run all dependency checks
            service_health = await self.dependency_checker.check_all_services(**service_urls)
            
            duration_ms = round((time.time() - start_time) * 1000, 2)
            
            logger.info(f"Health checks completed in {duration_ms}ms")
            
            return {
                "services": service_health,
                "duration_ms": duration_ms,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}", exc_info=True)
            raise
    
    async def check_critical_dependencies(self) -> Dict[str, Any]:
        """Check only critical dependencies for readiness probe"""
        start_time = time.time()
        
        try:
            # Check only critical services
            tasks = [
                self.dependency_checker.check_aiml_service(settings.aiml_service_url),
                self.dependency_checker.check_data_layer(settings.data_layer_url)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            critical_services = {}
            failed_services = []
            
            for result in results:
                if isinstance(result, Exception):
                    failed_services.append(f"unknown_service: {str(result)}")
                else:
                    service_name = result["service"]
                    critical_services[service_name] = result
                    
                    if result["status"] != "healthy":
                        failed_services.append(service_name)
            
            all_critical_healthy = len(failed_services) == 0
            duration_ms = round((time.time() - start_time) * 1000, 2)
            
            return {
                "all_critical_healthy": all_critical_healthy,
                "critical_services": critical_services,
                "failed_services": failed_services,
                "duration_ms": duration_ms
            }
            
        except Exception as e:
            logger.error(f"Critical dependency check failed: {e}")
            return {
                "all_critical_healthy": False,
                "critical_services": {},
                "failed_services": ["health_check_system"],
                "error": str(e)
            }
    
    async def check_single_service(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Check health of a single service"""
        try:
            if service_name == "aiml-orchestration":
                return await self.dependency_checker.check_aiml_service(settings.aiml_service_url)
            elif service_name == "data-layer":
                return await self.dependency_checker.check_data_layer(settings.data_layer_url)
            elif service_name == "redis":
                return await self.dependency_checker.check_redis(settings.redis_url)
            elif service_name == "postgresql":
                postgres_url = getattr(settings, 'postgres_url', None)
                return await self.dependency_checker.check_postgres(postgres_url)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Single service check failed for {service_name}: {e}")
            return {
                "service": service_name,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_available_services(self) -> List[str]:
        """Get list of available services for health checks"""
        return ["aiml-orchestration", "data-layer", "redis", "postgresql"]
    
    def get_service_summary(self, service_health: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of service health"""
        total_services = len(service_health)
        healthy_services = len([s for s in service_health.values() if s.get("status") == "healthy"])
        critical_failures = [
            name for name, health in service_health.items() 
            if health.get("status") != "healthy" and health.get("critical", True)
        ]
        
        return {
            "total_services": total_services,
            "healthy_services": healthy_services,
            "unhealthy_services": total_services - healthy_services,
            "critical_failures": critical_failures,
            "overall_health_percentage": round((healthy_services / total_services) * 100, 1) if total_services > 0 else 0
        }


# Global instance
_health_service: Optional[HealthService] = None


def get_health_service() -> HealthService:
    """Get health service instance (singleton pattern)"""
    global _health_service
    
    if _health_service is None:
        _health_service = HealthService()
    
    return _health_service