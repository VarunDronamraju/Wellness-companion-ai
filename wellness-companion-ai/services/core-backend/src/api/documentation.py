# ========================================
# services/core-backend/src/api/documentation.py
# ========================================

"""
FastAPI Documentation Configuration - Enhanced OpenAPI setup
Configures comprehensive API documentation with examples and metadata
"""

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from typing import Dict, Any, Optional

from docs.api_description import get_openapi_metadata
from docs.tags_metadata import get_tags_metadata
from docs.examples import get_request_examples, get_response_examples



def configure_openapi_documentation(app: FastAPI) -> None:
    """Configure enhanced OpenAPI documentation for the FastAPI app"""
    
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        
        # Get base OpenAPI schema
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
        
        # Enhanced metadata
        metadata = get_openapi_metadata()
        openapi_schema.update({
            "info": {
                **openapi_schema["info"],
                **metadata
            }
        })
        
        # Add enhanced error responses to all endpoints
        add_common_responses(openapi_schema)
        
        # Add request/response examples
        add_examples_to_schema(openapi_schema)
        
        # Add security schemes
        add_security_schemes(openapi_schema)
        
        # Cache the schema
        app.openapi_schema = openapi_schema
        return app.openapi_schema
    
    # Set custom OpenAPI function
    app.openapi = custom_openapi
    
    # Set tags metadata
    app.openapi_tags = get_tags_metadata()


def add_common_responses(openapi_schema: Dict[str, Any]) -> None:
    """Add common error responses to all endpoints"""
    
    common_responses = {
        "400": {
            "description": "Bad Request - Invalid request parameters",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "success": {"type": "boolean", "example": False},
                            "error": {"type": "string", "example": "Invalid request parameters"},
                            "error_code": {"type": "string", "example": "BAD_REQUEST"},
                            "details": {"type": "object"},
                            "request_id": {"type": "string", "example": "req_12345678-90ab-cdef-1234-567890abcdef"},
                            "timestamp": {"type": "string", "format": "date-time"}
                        }
                    }
                }
            }
        }
    }
    
    # Add common responses to all paths
    if "paths" in openapi_schema:
        for path, methods in openapi_schema["paths"].items():
            for method, operation in methods.items():
                if isinstance(operation, dict) and "responses" in operation:
                    # Add common error responses that aren't already defined
                    for status_code, response in common_responses.items():
                        if status_code not in operation["responses"]:
                            operation["responses"][status_code] = response


def add_examples_to_schema(openapi_schema: Dict[str, Any]) -> None:
    """Add request and response examples to the OpenAPI schema"""
    
    request_examples = get_request_examples()
    response_examples = get_response_examples()
    
    # This would be more complex in a real implementation
    # For now, we'll add examples at the schema level
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}
    
    if "examples" not in openapi_schema["components"]:
        openapi_schema["components"]["examples"] = {}
    
    # Add request examples
    for example_name, example_data in request_examples.items():
        openapi_schema["components"]["examples"][f"request_{example_name}"] = example_data
    
    # Add response examples  
    for example_name, example_data in response_examples.items():
        openapi_schema["components"]["examples"][f"response_{example_name}"] = example_data


def add_security_schemes(openapi_schema: Dict[str, Any]) -> None:
    """Add security schemes to the OpenAPI schema"""
    
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}
    
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT token obtained from the authentication endpoint"
        },
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API key for service-to-service authentication"
        },
        "OAuth2": {
            "type": "oauth2",
            "description": "OAuth2 authentication flow",
            "flows": {
                "authorizationCode": {
                    "authorizationUrl": "/api/auth/oauth/authorize",
                    "tokenUrl": "/api/auth/oauth/token",
                    "scopes": {
                        "read": "Read access to resources",
                        "write": "Write access to resources", 
                        "admin": "Administrative access"
                    }
                }
            }
        }
    }
    
    # Add global security requirement
    openapi_schema["security"] = [
        {"BearerAuth": []},
        {"ApiKeyAuth": []},
        {"OAuth2": ["read", "write"]}
    ]
