# ========================================
# services/core-backend/src/api/middleware/error_responses.py
# ========================================

"""
Error Response Formats - Standardized error response models and utilities
Ensures consistent error format across all API endpoints
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class ErrorDetail(BaseModel):
    """Individual error detail"""
    field: Optional[str] = Field(None, description="Field that caused the error")
    message: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Specific error code")
    value: Optional[Any] = Field(None, description="Invalid value that caused error")


class StandardErrorResponse(BaseModel):
    """Standard API error response format"""
    success: bool = Field(False, description="Request success status")
    error: str = Field(..., description="Main error message")
    error_code: str = Field(..., description="Machine-readable error code")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional error details")
    request_id: str = Field(..., description="Unique request identifier")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    
    # Optional debug information (development only)
    debug: Optional[Dict[str, Any]] = Field(None, description="Debug information")
    stack_trace: Optional[str] = Field(None, description="Exception stack trace")


class ValidationErrorResponse(StandardErrorResponse):
    """Validation error response with field-specific errors"""
    validation_errors: List[ErrorDetail] = Field(default_factory=list, description="Field validation errors")
    total_errors: int = Field(0, description="Total number of validation errors")


class ServiceErrorResponse(StandardErrorResponse):
    """External service error response"""
    service_name: str = Field(..., description="Name of the failing service")
    service_status: Optional[str] = Field(None, description="Service status")
    retry_after: Optional[int] = Field(None, description="Retry after seconds")


class RateLimitErrorResponse(StandardErrorResponse):
    """Rate limit error response"""
    limit: int = Field(..., description="Rate limit")
    window: str = Field(..., description="Rate limit window")
    reset_time: Optional[str] = Field(None, description="When rate limit resets")
    retry_after: int = Field(..., description="Seconds until retry allowed")


def create_standard_error(
    message: str,
    error_code: str,
    status_code: int = 500,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
    include_debug: bool = False
) -> Dict[str, Any]:
    """Create a standard error response dictionary"""
    
    if not request_id:
        request_id = str(uuid.uuid4())
    
    error_response = StandardErrorResponse(
        error=message,
        error_code=error_code,
        details=details or {},
        request_id=request_id
    )
    
    response_dict = error_response.dict()
    response_dict["status_code"] = status_code
    
    if not include_debug:
        response_dict.pop("debug", None)
        response_dict.pop("stack_trace", None)
    
    return response_dict


def create_validation_error(
    message: str = "Validation failed",
    validation_errors: Optional[List[Dict[str, Any]]] = None,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """Create a validation error response"""
    
    if not request_id:
        request_id = str(uuid.uuid4())
    
    errors = []
    if validation_errors:
        for error in validation_errors:
            errors.append(ErrorDetail(**error))
    
    error_response = ValidationErrorResponse(
        error=message,
        error_code="VALIDATION_ERROR",
        validation_errors=errors,
        total_errors=len(errors),
        request_id=request_id
    )
    
    response_dict = error_response.dict()
    response_dict["status_code"] = 422
    
    return response_dict

