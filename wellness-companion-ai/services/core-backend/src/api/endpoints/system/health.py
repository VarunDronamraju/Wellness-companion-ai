"""Health Check API"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any
import logging
from datetime import datetime
import httpx
import asyncio
import time

logger = logging.getLogger(__name__)
router = APIRouter()

async def check_aiml_service():
    """Check AI/ML service health"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://aiml-orchestration:8000/health")
            return {
                "service": "aiml-orchestration",
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_code": response.status_code,
                "response_time_ms": 0
            }
    except Exception as e:
        return {
            "service": "aiml-orchestration", 
            "status": "unhealthy",
            "error": str(e)
        }

async def check_data_layer():
    """Check Data Layer service health"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://data-layer:8000/health")
            return {
                "service": "data-layer",
                "status": "healthy" if response.status_code == 200 else "unhealthy", 
                "response_code": response.status_code
            }
    except Exception as e:
        return {
            "service": "data-layer",
            "status": "unhealthy", 
            "error": str(e)
        }

@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with dependency validation"""
    try:
        start_time = time.time()
        
        # Check all services concurrently
        tasks = [
            check_aiml_service(),
            check_data_layer()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        services = {}
        overall_status = "healthy"
        
        for result in results:
            if isinstance(result, Exception):
                overall_status = "unhealthy"
                services["unknown"] = {"status": "error", "error": str(result)}
            else:
                services[result["service"]] = result
                if result["status"] != "healthy":
                    overall_status = "unhealthy"
        
        duration_ms = round((time.time() - start_time) * 1000, 2)
        
        response = {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "service": "core-backend",
            "version": "1.0.0",
            "dependencies": services,
            "check_duration_ms": duration_ms
        }
        
        status_code = 200 if overall_status == "healthy" else 503
        return JSONResponse(status_code=status_code, content=response)
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
        )

@router.get("/health/live")
async def liveness_probe():
    """Liveness probe endpoint"""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/health/ready")
async def readiness_probe():
    """Readiness probe endpoint"""
    try:
        aiml_check = await check_aiml_service()
        
        if aiml_check["status"] == "healthy":
            return JSONResponse(
                status_code=200,
                content={
                    "status": "ready",
                    "timestamp": datetime.utcnow().isoformat(),
                    "critical_services": {"aiml-orchestration": aiml_check}
                }
            )
        else:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "not_ready",
                    "timestamp": datetime.utcnow().isoformat(),
                    "failed_services": ["aiml-orchestration"]
                }
            )
            
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

@router.get("/health/services/{service_name}")
async def service_health_check(service_name: str):
    """Check health of specific service"""
    try:
        if service_name == "aiml-orchestration":
            result = await check_aiml_service()
        elif service_name == "data-layer":
            result = await check_data_layer()
        else:
            return JSONResponse(
                status_code=404,
                content={
                    "error": f"Service '{service_name}' not found",
                    "available_services": ["aiml-orchestration", "data-layer"]
                }
            )
        
        status_code = 200 if result["status"] == "healthy" else 503
        return JSONResponse(status_code=status_code, content=result)
        
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": service_name,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )