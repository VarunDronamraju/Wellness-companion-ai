# ========================================
# services/core-backend/src/api/middleware/exception_mapper.py
# ========================================

"""
Exception Mapper - Maps exceptions to appropriate HTTP status codes and responses
Provides consistent error handling across all API endpoints
"""

from typing import Dict, Any, Optional, Tuple, Type
import logging
from datetime import datetime
import traceback
import uuid

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from ...core.exceptions import (
    WellnessCompanionException,
    AuthenticationError,
    AuthorizationError,
    DocumentNotFoundError,
    DocumentError,
    SearchError,
    ExternalServiceError,
    ValidationError as CustomValidationError,
    RateLimitExceededError,
    SystemError,
    MaintenanceModeError,
    handle_pydantic_validation_error,
    log_exception
)

logger = logging.getLogger(__name__)


class ExceptionMapper:
    """Maps exceptions to HTTP responses with proper status codes and formatting"""
    
    def __init__(self):
        # Exception type to status code mapping
        self.exception_status_map: Dict[Type[Exception], int] = {
            # Custom application exceptions (already have status_code)
            WellnessCompanionException: None,  # Use exception's status_code
            
            # FastAPI/HTTP exceptions
            HTTPException: None,  # Use exception's status_code
            
            # Pydantic validation errors
            ValidationError: 422,
            
            # Python built-in exceptions
            ValueError: 400,
            TypeError: 400,
            KeyError: 400,
            AttributeError: 500,
            FileNotFoundError: 404,
            PermissionError: 403,
            TimeoutError: 408,
            ConnectionError: 503,
            
            # Default for unknown exceptions
            Exception: 500
        }
        
        # Error code mapping for common exceptions
        self.error_code_map: Dict[Type[Exception], str] = {
            ValueError: "INVALID_VALUE",
            TypeError: "INVALID_TYPE",
            KeyError: "MISSING_KEY",
            AttributeError: "ATTRIBUTE_ERROR",
            FileNotFoundError: "FILE_NOT_FOUND",
            PermissionError: "PERMISSION_DENIED",
            TimeoutError: "REQUEST_TIMEOUT",
            ConnectionError: "SERVICE_UNAVAILABLE",
            Exception: "INTERNAL_SERVER_ERROR"
        }
    
    def map_exception_to_response(
        self,
        exc: Exception,
        request: Optional[Request] = None,
        request_id: Optional[str] = None
    ) -> JSONResponse:
        """
        Map an exception to a standardized JSON response
        
        Args:
            exc: The exception to map
            request: Optional FastAPI request object
            request_id: Optional request identifier
            
        Returns:
            JSONResponse: Standardized error response
        """
        # Generate request ID if not provided
        if not request_id:
            request_id = str(uuid.uuid4())
        
        # Extract user context if available
        user_id = None
        if request and hasattr(request.state, 'user_id'):
            user_id = request.state.user_id
        
        # Log the exception with context
        log_exception(exc, request_id=request_id, user_id=user_id)
        
        # Handle different exception types
        if isinstance(exc, WellnessCompanionException):
            return self._handle_application_exception(exc, request_id)
        elif isinstance(exc, HTTPException):
            return self._handle_http_exception(exc, request_id)
        elif isinstance(exc, ValidationError):
            return self._handle_pydantic_validation_error(exc, request_id)
        else:
            return self._handle_generic_exception(exc, request_id)
    
    def _handle_application_exception(
        self,
        exc: WellnessCompanionException,
        request_id: str
    ) -> JSONResponse:
        """Handle custom application exceptions"""
        
        response_data = {
            "success": False,
            "error": exc.message,
            "error_code": exc.error_code,
            "details": exc.details,
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add stack trace in development mode
        if self._is_development_mode():
            response_data["stack_trace"] = traceback.format_exc()
        
        return JSONResponse(
            status_code=exc.status_code,
            content=response_data
        )
    
    def _handle_http_exception(
        self,
        exc: HTTPException,
        request_id: str
    ) -> JSONResponse:
        """Handle FastAPI HTTP exceptions"""
        
        # Extract error details if available
        details = {}
        if hasattr(exc, 'detail') and isinstance(exc.detail, dict):
            details = exc.detail
            error_message = details.get('message', 'HTTP exception occurred')
        else:
            error_message = str(exc.detail) if exc.detail else 'HTTP exception occurred'
        
        response_data = {
            "success": False,
            "error": error_message,
            "error_code": f"HTTP_{exc.status_code}",
            "details": details,
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return JSONResponse(
            status_code=exc.status_code,
            content=response_data
        )
    
    def _handle_pydantic_validation_error(
        self,
        exc: ValidationError,
        request_id: str
    ) -> JSONResponse:
        """Handle Pydantic validation errors"""
        
        validation_data = handle_pydantic_validation_error(exc)
        
        response_data = {
            "success": False,
            "error": validation_data['error'],
            "error_code": validation_data['error_code'],
            "details": validation_data['details'],
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return JSONResponse(
            status_code=422,
            content=response_data
        )
    
    def _handle_generic_exception(
        self,
        exc: Exception,
        request_id: str
    ) -> JSONResponse:
        """Handle generic Python exceptions"""
        
        exc_type = type(exc)
        status_code = self.exception_status_map.get(exc_type, 500)
        error_code = self.error_code_map.get(exc_type, "INTERNAL_SERVER_ERROR")
        
        # Create user-friendly error message
        if status_code == 500:
            # Don't expose internal error details to users
            error_message = "An internal server error occurred"
            user_details = {
                "message": "The server encountered an unexpected condition that prevented it from fulfilling the request."
            }
        else:
            error_message = str(exc)
            user_details = {
                "exception_type": exc_type.__name__,
                "message": str(exc)
            }
        
        response_data = {
            "success": False,
            "error": error_message,
            "error_code": error_code,
            "details": user_details,
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add debug information in development mode
        if self._is_development_mode():
            response_data["debug"] = {
                "exception_type": exc_type.__name__,
                "exception_message": str(exc),
                "stack_trace": traceback.format_exc()
            }
        
        return JSONResponse(
            status_code=status_code,
            content=response_data
        )
    
    def _is_development_mode(self) -> bool:
        """Check if running in development mode"""
        import os
        return os.getenv("ENVIRONMENT", "development").lower() == "development"
    
    def get_error_details_for_status_code(self, status_code: int) -> Dict[str, str]:
        """Get standard error details for HTTP status codes"""
        
        status_messages = {
            400: "Bad Request - The request could not be understood by the server",
            401: "Unauthorized - Authentication is required",
            403: "Forbidden - Access to the resource is denied",
            404: "Not Found - The requested resource was not found",
            405: "Method Not Allowed - The HTTP method is not supported",
            408: "Request Timeout - The request took too long to process",
            409: "Conflict - The request conflicts with the current state",
            413: "Payload Too Large - The request payload is too large",
            415: "Unsupported Media Type - The media type is not supported",
            422: "Unprocessable Entity - The request contains invalid data",
            429: "Too Many Requests - Rate limit exceeded",
            500: "Internal Server Error - An unexpected server error occurred",
            501: "Not Implemented - The functionality is not implemented",
            502: "Bad Gateway - Invalid response from upstream server",
            503: "Service Unavailable - The service is temporarily unavailable",
            504: "Gateway Timeout - Timeout waiting for upstream server"
        }
        
        return {
            "status_code": status_code,
            "description": status_messages.get(status_code, "Unknown error")
        }


# Global exception mapper instance
exception_mapper = ExceptionMapper()


def create_error_response(
    message: str,
    error_code: str,
    status_code: int = 500,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
) -> JSONResponse:
    """
    Create a standardized error response
    
    Args:
        message: Error message
        error_code: Error code
        status_code: HTTP status code
        details: Additional error details
        request_id: Request identifier
        
    Returns:
        JSONResponse: Standardized error response
    """
    if not request_id:
        request_id = str(uuid.uuid4())
    
    response_data = {
        "success": False,
        "error": message,
        "error_code": error_code,
        "details": details or {},
        "request_id": request_id,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return JSONResponse(
        status_code=status_code,
        content=response_data
    )