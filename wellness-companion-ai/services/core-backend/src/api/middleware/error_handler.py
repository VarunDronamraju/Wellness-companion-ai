
# ========================================
# services/core-backend/src/api/middleware/error_handler.py
# ========================================

"""
Global Error Handler - FastAPI middleware for centralized error handling
Catches all unhandled exceptions and formats them consistently
"""

import logging
import traceback
import uuid
from typing import Callable, Optional
from datetime import datetime

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import ValidationError
import asyncio

from src.api.middleware.exception_mapper import exception_mapper, create_error_response
from src.api.middleware.error_responses import create_standard_error
from src.core.exceptions import (
    WellnessCompanionException,
    SystemError,
    MaintenanceModeError,
    log_exception
)

logger = logging.getLogger(__name__)


class GlobalErrorHandler(BaseHTTPMiddleware):
    """Global error handling middleware"""
    
    def __init__(
        self,
        app: FastAPI,
        include_debug_info: bool = False,
        log_all_exceptions: bool = True
    ):
        super().__init__(app)
        self.include_debug_info = include_debug_info
        self.log_all_exceptions = log_all_exceptions
        self.startup_time = datetime.utcnow()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and handle any exceptions"""
        
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Add request start time
        start_time = datetime.utcnow()
        request.state.start_time = start_time
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Add timing and request ID headers
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Processing-Time"] = f"{processing_time:.3f}s"
            
            return response
            
        except Exception as exc:
            # Handle any unhandled exceptions
            return await self._handle_exception(exc, request, request_id)
    
    async def _handle_exception(
        self,
        exc: Exception,
        request: Request,
        request_id: str
    ) -> JSONResponse:
        """Handle exceptions and return appropriate error response"""
        
        try:
            # Log exception with context
            self._log_exception_with_context(exc, request, request_id)
            
            # Use exception mapper to create response
            return exception_mapper.map_exception_to_response(
                exc=exc,
                request=request,
                request_id=request_id
            )
            
        except Exception as handler_exc:
            # If error handler itself fails, return basic error response
            logger.critical(
                f"Error handler failed: {handler_exc}",
                extra={
                    "original_exception": str(exc),
                    "handler_exception": str(handler_exc),
                    "request_id": request_id
                }
            )
            
            return self._create_fallback_error_response(request_id)
    
    def _log_exception_with_context(
        self,
        exc: Exception,
        request: Request,
        request_id: str
    ) -> None:
        """Log exception with request context"""
        
        if not self.log_all_exceptions:
            return
        
        # Extract request context
        context = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent", "unknown"),
            "exception_type": type(exc).__name__
        }
        
        # Add user context if available
        if hasattr(request.state, 'user_id'):
            context["user_id"] = request.state.user_id
        
        # Add timing information
        if hasattr(request.state, 'start_time'):
            processing_time = (datetime.utcnow() - request.state.start_time).total_seconds()
            context["processing_time"] = f"{processing_time:.3f}s"
        
        # Log based on exception type
        if isinstance(exc, WellnessCompanionException):
            if exc.status_code >= 500:
                logger.error(f"Application error: {exc.message}", extra=context)
            else:
                logger.warning(f"Client error: {exc.message}", extra=context)
        else:
            logger.exception(f"Unhandled exception: {exc}", extra=context)
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request"""
        
        # Check for forwarded headers (proxy/load balancer)
        forwarded_ips = request.headers.get("x-forwarded-for")
        if forwarded_ips:
            return forwarded_ips.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _create_fallback_error_response(self, request_id: str) -> JSONResponse:
        """Create a basic error response when error handler fails"""
        
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Internal server error",
                "error_code": "INTERNAL_SERVER_ERROR",
                "details": {
                    "message": "An unexpected error occurred while processing your request"
                },
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )


class HealthCheckErrorHandler:
    """Specialized error handler for health check endpoints"""
    
    @staticmethod
    def create_health_error_response(
        service_name: str,
        error_message: str,
        status_code: int = 503
    ) -> JSONResponse:
        """Create health check error response"""
        
        return JSONResponse(
            status_code=status_code,
            content={
                "service": service_name,
                "status": "unhealthy",
                "error": error_message,
                "timestamp": datetime.utcnow().isoformat(),
                "uptime": "unknown"
            }
        )


def setup_error_handling(app: FastAPI, debug: bool = False) -> None:
    """Setup global error handling for FastAPI application"""
    
    # Add global error handler middleware
    app.add_middleware(
        GlobalErrorHandler,
        include_debug_info=debug,
        log_all_exceptions=True
    )
    
    # Add specific exception handlers for common cases
    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError):
        """Handle Pydantic validation errors"""
        request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
        return exception_mapper.map_exception_to_response(exc, request, request_id)
    
    @app.exception_handler(WellnessCompanionException)
    async def wellness_exception_handler(request: Request, exc: WellnessCompanionException):
        """Handle custom application exceptions"""
        request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
        return exception_mapper.map_exception_to_response(exc, request, request_id)
    
    @app.exception_handler(MaintenanceModeError)
    async def maintenance_exception_handler(request: Request, exc: MaintenanceModeError):
        """Handle maintenance mode"""
        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "error": "Service temporarily unavailable",
                "error_code": "MAINTENANCE_MODE",
                "details": {
                    "message": exc.message,
                    "maintenance_info": "The service is currently under maintenance. Please try again later."
                },
                "request_id": getattr(request.state, 'request_id', str(uuid.uuid4())),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    logger.info("Global error handling configured successfully")
