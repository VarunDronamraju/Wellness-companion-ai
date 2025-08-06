
# ========================================
# services/core-backend/src/api/middleware/__init__.py
# ========================================

"""
Middleware Package - FastAPI middleware components
Provides error handling, CORS, rate limiting, and request processing
"""

from src.api.middleware.error_handler import GlobalErrorHandler, setup_error_handling, HealthCheckErrorHandler
from src.api.middleware.exception_mapper import ExceptionMapper, exception_mapper, create_error_response
from src.api.middleware.error_responses import (
    StandardErrorResponse,
    ValidationErrorResponse,
    ServiceErrorResponse,
    RateLimitErrorResponse,
    ErrorDetail,
    create_standard_error,
    create_validation_error
)

__all__ = [
    # Error handling
    "GlobalErrorHandler",
    "setup_error_handling",
    "HealthCheckErrorHandler",
    
    # Exception mapping
    "ExceptionMapper",
    "exception_mapper",
    "create_error_response",
    
    # Response models
    "StandardErrorResponse",
    "ValidationErrorResponse", 
    "ServiceErrorResponse",
    "RateLimitErrorResponse",
    "ErrorDetail",
    "create_standard_error",
    "create_validation_error"
]