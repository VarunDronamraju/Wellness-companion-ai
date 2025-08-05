"""
Integration Exceptions - Wellness Companion AI
Custom exceptions for external service integrations
"""

from typing import Optional, Dict, Any
import httpx


class IntegrationException(Exception):
    """Base exception for integration errors"""
    
    def __init__(
        self, 
        message: str, 
        service: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.service = service
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)


class ServiceUnavailableException(IntegrationException):
    """Raised when external service is unavailable"""
    pass


class ServiceTimeoutException(IntegrationException):
    """Raised when external service times out"""
    pass


class ServiceAuthenticationException(IntegrationException):
    """Raised when authentication with external service fails"""
    pass


class ServiceValidationException(IntegrationException):
    """Raised when external service returns validation errors"""
    pass


class AIMLServiceException(IntegrationException):
    """Specific exception for AI/ML service errors"""
    
    def __init__(
        self, 
        message: str, 
        operation: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None
    ):
        self.operation = operation
        super().__init__(
            message=message,
            service="aiml-orchestration",
            status_code=status_code,
            response_data=response_data
        )


def handle_httpx_exception(exc: httpx.HTTPError, service: str) -> IntegrationException:
    """Convert httpx exceptions to integration exceptions"""
    
    if isinstance(exc, httpx.TimeoutException):
        return ServiceTimeoutException(
            message=f"Timeout while connecting to {service}",
            service=service
        )
    
    elif isinstance(exc, httpx.ConnectError):
        return ServiceUnavailableException(
            message=f"Cannot connect to {service} - service may be down",
            service=service
        )
    
    elif isinstance(exc, httpx.HTTPStatusError):
        status_code = exc.response.status_code
        
        if status_code == 401:
            return ServiceAuthenticationException(
                message=f"Authentication failed with {service}",
                service=service,
                status_code=status_code
            )
        
        elif status_code == 422:
            return ServiceValidationException(
                message=f"Validation error from {service}",
                service=service,
                status_code=status_code,
                response_data=exc.response.json() if exc.response.content else None
            )
        
        elif status_code >= 500:
            return ServiceUnavailableException(
                message=f"Server error from {service}: {status_code}",
                service=service,
                status_code=status_code
            )
        
        else:
            return IntegrationException(
                message=f"HTTP error from {service}: {status_code}",
                service=service,
                status_code=status_code
            )
    
    else:
        return IntegrationException(
            message=f"Unexpected error with {service}: {str(exc)}",
            service=service
        )