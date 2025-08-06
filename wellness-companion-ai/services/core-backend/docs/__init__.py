# ========================================
# services/core-backend/docs/__init__.py
# ========================================

"""
API Documentation Package - Enhanced OpenAPI documentation components
Provides rich, interactive documentation for all API endpoints
"""

from .api_description import get_api_description
from .tags_metadata import get_tags_metadata
from .examples import get_request_examples, get_response_examples

__all__ = [
    "get_api_description",
    "get_tags_metadata", 
    "get_request_examples",
    "get_response_examples"
]

