# ========================================
# services/core-backend/src/core/exceptions.py
# ========================================

"""
Custom Application Exceptions - Domain-specific error handling
Provides structured exception hierarchy for consistent error handling
"""

from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class WellnessCompanionException(Exception):
    """Base exception for all Wellness Companion errors"""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500
    ):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API response"""
        return {
            "error": self.message,
            "error_code": self.error_code,
            "details": self.details,
            "type": self.__class__.__name__
        }


# === AUTHENTICATION EXCEPTIONS ===

class AuthenticationError(WellnessCompanionException):
    """Authentication-related errors"""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, status_code=401, **kwargs)


class AuthorizationError(WellnessCompanionException):
    """Authorization/permission errors"""
    
    def __init__(self, message: str = "Access denied", **kwargs):
        super().__init__(message, status_code=403, **kwargs)


class TokenExpiredError(AuthenticationError):
    """JWT token expired"""
    
    def __init__(self, message: str = "Token has expired", **kwargs):
        super().__init__(message, error_code="TOKEN_EXPIRED", **kwargs)


class InvalidTokenError(AuthenticationError):
    """Invalid JWT token"""
    
    def __init__(self, message: str = "Invalid token", **kwargs):
        super().__init__(message, error_code="INVALID_TOKEN", **kwargs)


# === DOCUMENT EXCEPTIONS ===

class DocumentError(WellnessCompanionException):
    """Document-related errors"""
    
    def __init__(self, message: str, document_id: Optional[str] = None, **kwargs):
        details = kwargs.get('details', {})
        if document_id:
            details['document_id'] = document_id
        kwargs['details'] = details
        super().__init__(message, **kwargs)


class DocumentNotFoundError(DocumentError):
    """Document not found"""
    
    def __init__(self, document_id: str, **kwargs):
        message = f"Document '{document_id}' not found"
        super().__init__(
            message, 
            document_id=document_id,
            error_code="DOCUMENT_NOT_FOUND",
            status_code=404,
            **kwargs
        )


class DocumentAccessDeniedError(DocumentError):
    """User doesn't have access to document"""
    
    def __init__(self, document_id: str, user_id: str, **kwargs):
        message = f"Access denied to document '{document_id}'"
        details = kwargs.get('details', {})
        details.update({'document_id': document_id, 'user_id': user_id})
        super().__init__(
            message,
            error_code="DOCUMENT_ACCESS_DENIED",
            status_code=403,
            details=details,
            **kwargs
        )


class DocumentProcessingError(DocumentError):
    """Document processing failed"""
    
    def __init__(self, document_id: str, stage: str, **kwargs):
        message = f"Document processing failed at stage: {stage}"
        details = kwargs.get('details', {})
        details.update({'document_id': document_id, 'failed_stage': stage})
        super().__init__(
            message,
            error_code="DOCUMENT_PROCESSING_FAILED",
            status_code=422,
            details=details,
            **kwargs
        )


class DocumentTooLargeError(DocumentError):
    """Document exceeds size limits"""
    
    def __init__(self, size: int, max_size: int, **kwargs):
        size_mb = size / (1024 * 1024)
        max_mb = max_size / (1024 * 1024)
        message = f"Document too large ({size_mb:.1f}MB). Maximum allowed: {max_mb:.1f}MB"
        details = kwargs.get('details', {})
        details.update({'size_bytes': size, 'max_size_bytes': max_size})
        super().__init__(
            message,
            error_code="DOCUMENT_TOO_LARGE",
            status_code=413,
            details=details,
            **kwargs
        )


class UnsupportedFileTypeError(DocumentError):
    """Unsupported file type"""
    
    def __init__(self, file_type: str, supported_types: List[str], **kwargs):
        message = f"File type '{file_type}' not supported. Supported types: {', '.join(supported_types)}"
        details = kwargs.get('details', {})
        details.update({'file_type': file_type, 'supported_types': supported_types})
        super().__init__(
            message,
            error_code="UNSUPPORTED_FILE_TYPE",
            status_code=415,
            details=details,
            **kwargs
        )


# === SEARCH EXCEPTIONS ===

class SearchError(WellnessCompanionException):
    """Search-related errors"""
    
    def __init__(self, message: str, query: Optional[str] = None, **kwargs):
        details = kwargs.get('details', {})
        if query:
            details['query'] = query
        kwargs['details'] = details
        super().__init__(message, **kwargs)


class SearchTimeoutError(SearchError):
    """Search operation timed out"""
    
    def __init__(self, query: str, timeout_seconds: int, **kwargs):
        message = f"Search timed out after {timeout_seconds} seconds"
        super().__init__(
            message,
            query=query,
            error_code="SEARCH_TIMEOUT",
            status_code=408,
            **kwargs
        )


class NoSearchResultsError(SearchError):
    """No search results found"""
    
    def __init__(self, query: str, **kwargs):
        message = f"No results found for query: '{query}'"
        super().__init__(
            message,
            query=query,
            error_code="NO_SEARCH_RESULTS",
            status_code=404,
            **kwargs
        )


class SearchServiceUnavailableError(SearchError):
    """Search service unavailable"""
    
    def __init__(self, service_name: str, **kwargs):
        message = f"Search service '{service_name}' is currently unavailable"
        details = kwargs.get('details', {})
        details['service_name'] = service_name
        super().__init__(
            message,
            error_code="SEARCH_SERVICE_UNAVAILABLE",
            status_code=503,
            details=details,
            **kwargs
        )


# === EXTERNAL SERVICE EXCEPTIONS ===

class ExternalServiceError(WellnessCompanionException):
    """External service integration errors"""
    
    def __init__(self, service_name: str, message: str, **kwargs):
        details = kwargs.get('details', {})
        details['service_name'] = service_name
        kwargs['details'] = details
        super().__init__(message, **kwargs)


class AIMLServiceError(ExternalServiceError):
    """AI/ML service errors"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            "aiml-orchestration",
            message,
            error_code="AIML_SERVICE_ERROR",
            status_code=502,
            **kwargs
        )


class DataLayerError(ExternalServiceError):
    """Data layer service errors"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            "data-layer",
            message,
            error_code="DATA_LAYER_ERROR",
            status_code=502,
            **kwargs
        )


class WebSearchAPIError(ExternalServiceError):
    """Web search API errors (Tavily, etc.)"""
    
    def __init__(self, message: str, api_name: str = "tavily", **kwargs):
        details = kwargs.get('details', {})
        details['api_name'] = api_name
        super().__init__(
            api_name,
            message,
            error_code="WEB_SEARCH_API_ERROR",
            status_code=502,
            details=details,
            **kwargs
        )


# === VALIDATION EXCEPTIONS ===

class ValidationError(WellnessCompanionException):
    """Data validation errors"""
    
    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        details = kwargs.get('details', {})
        if field:
            details['field'] = field
        kwargs['details'] = details
        super().__init__(
            message,
            error_code="VALIDATION_ERROR",
            status_code=422,
            **kwargs
        )


class RateLimitExceededError(WellnessCompanionException):
    """Rate limit exceeded"""
    
    def __init__(self, limit: int, window: str, **kwargs):
        message = f"Rate limit exceeded: {limit} requests per {window}"
        details = kwargs.get('details', {})
        details.update({'limit': limit, 'window': window})
        super().__init__(
            message,
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details=details,
            **kwargs
        )


# === SYSTEM EXCEPTIONS ===

class SystemError(WellnessCompanionException):
    """System-level errors"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            error_code="SYSTEM_ERROR",
            status_code=500,
            **kwargs
        )


class DatabaseError(SystemError):
    """Database connection/operation errors"""
    
    def __init__(self, message: str, operation: Optional[str] = None, **kwargs):
        details = kwargs.get('details', {})
        if operation:
            details['operation'] = operation
        super().__init__(
            message,
            error_code="DATABASE_ERROR",
            details=details,
            **kwargs
        )


class ConfigurationError(SystemError):
    """Configuration-related errors"""
    
    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        details = kwargs.get('details', {})
        if config_key:
            details['config_key'] = config_key
        super().__init__(
            message,
            error_code="CONFIGURATION_ERROR",
            details=details,
            **kwargs
        )


class MaintenanceModeError(WellnessCompanionException):
    """System in maintenance mode"""
    
    def __init__(self, message: str = "System is currently under maintenance", **kwargs):
        super().__init__(
            message,
            error_code="MAINTENANCE_MODE",
            status_code=503,
            **kwargs
        )


# === UTILITY FUNCTIONS ===

def handle_pydantic_validation_error(exc: Exception) -> Dict[str, Any]:
    """Convert Pydantic validation error to standard format"""
    
    errors = []
    if hasattr(exc, 'errors'):
        for error in exc.errors():
            field_path = ' -> '.join(str(loc) for loc in error['loc'])
            errors.append({
                'field': field_path,
                'message': error['msg'],
                'type': error['type'],
                'input': error.get('input', 'N/A')
            })
    
    return {
        'error': 'Validation failed',
        'error_code': 'VALIDATION_ERROR',
        'details': {
            'validation_errors': errors,
            'total_errors': len(errors)
        },
        'type': 'ValidationError'
    }


def log_exception(exc: Exception, request_id: Optional[str] = None, user_id: Optional[str] = None):
    """Log exception with context"""
    
    context = {
        'exception_type': type(exc).__name__,
        'exception_message': str(exc)
    }
    
    if request_id:
        context['request_id'] = request_id
    if user_id:
        context['user_id'] = user_id
    
    if isinstance(exc, WellnessCompanionException):
        context.update({
            'error_code': exc.error_code,
            'status_code': exc.status_code,
            'details': exc.details
        })
        logger.error(f"Application error: {exc.message}", extra=context)
    else:
        logger.exception(f"Unhandled exception: {exc}", extra=context)