
# ========================================
# services/core-backend/src/api/middleware/cors_handler.py
# ========================================

"""
Enhanced CORS Handler - Advanced CORS middleware with security features
Provides comprehensive CORS handling for desktop app communication
"""

import logging
import re
from typing import Sequence, Optional, List, Union
from urllib.parse import urlparse

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import PlainTextResponse

from src.core.cors_config import get_cors_config, CORSConfig
from src.core.security_config import get_security_config, SecurityConfig

logger = logging.getLogger(__name__)


class EnhancedCORSMiddleware(BaseHTTPMiddleware):
    """Enhanced CORS middleware with additional security features"""
    
    def __init__(
        self,
        app: FastAPI,
        cors_config: Optional[CORSConfig] = None,
        security_config: Optional[SecurityConfig] = None
    ):
        super().__init__(app)
        self.cors_config = cors_config or get_cors_config()
        self.security_config = security_config or get_security_config()
        
        # Compile regex patterns for performance
        self.origin_regex = None
        if self.cors_config.allowed_origins_regex:
            self.origin_regex = re.compile(self.cors_config.allowed_origins_regex)
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process CORS and security headers"""
        
        # Get origin from request
        origin = request.headers.get("origin")
        
        # Handle preflight requests
        if request.method == "OPTIONS":
            return await self._handle_preflight_request(request, origin)
        
        # Process actual request
        response = await call_next(request)
        
        # Add CORS headers to response
        self._add_cors_headers(response, origin)
        
        # Add security headers
        self._add_security_headers(response)
        
        return response
    
    async def _handle_preflight_request(self, request: Request, origin: Optional[str]) -> Response:
        """Handle CORS preflight requests"""
        
        # Check if origin is allowed
        if not self._is_origin_allowed(origin):
            logger.warning(f"CORS preflight: Origin not allowed: {origin}")
            return PlainTextResponse(
                "Origin not allowed",
                status_code=403,
                headers={"Vary": "Origin"}
            )
        
        # Get requested method and headers
        requested_method = request.headers.get("access-control-request-method")
        requested_headers = request.headers.get("access-control-request-headers", "")
        
        # Check if method is allowed
        if requested_method and requested_method not in self.cors_config.allowed_methods:
            logger.warning(f"CORS preflight: Method not allowed: {requested_method}")
            return PlainTextResponse(
                "Method not allowed",
                status_code=405,
                headers={"Vary": "Origin"}
            )
        
        # Prepare preflight response headers
        headers = {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": ", ".join(self.cors_config.allowed_methods),
            "Access-Control-Allow-Headers": ", ".join(self.cors_config.allowed_headers),
            "Access-Control-Max-Age": str(self.cors_config.max_age),
            "Vary": "Origin, Access-Control-Request-Method, Access-Control-Request-Headers"
        }
        
        # Add credentials header if enabled
        if self.cors_config.allow_credentials:
            headers["Access-Control-Allow-Credentials"] = "true"
        
        # Add exposed headers
        if self.cors_config.exposed_headers:
            headers["Access-Control-Expose-Headers"] = ", ".join(self.cors_config.exposed_headers)
        
        logger.debug(f"CORS preflight successful for origin: {origin}, method: {requested_method}")
        
        return PlainTextResponse(
            "",
            status_code=200,
            headers=headers
        )
    
    def _add_cors_headers(self, response: Response, origin: Optional[str]) -> None:
        """Add CORS headers to actual responses"""
        
        # Check if origin is allowed
        if not self._is_origin_allowed(origin):
            # Don't add CORS headers for disallowed origins
            response.headers["Vary"] = "Origin"
            return
        
        # Add CORS headers
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Vary"] = "Origin"
        
        # Add credentials header if enabled
        if self.cors_config.allow_credentials:
            response.headers["Access-Control-Allow-Credentials"] = "true"
        
        # Add exposed headers
        if self.cors_config.exposed_headers:
            response.headers["Access-Control-Expose-Headers"] = ", ".join(self.cors_config.exposed_headers)
    
    def _add_security_headers(self, response: Response) -> None:
        """Add security headers to response"""
        
        # Add all configured security headers
        for header_name, header_value in self.security_config.security_headers.items():
            response.headers[header_name] = header_value
        
        # Add custom security headers
        response.headers["X-Powered-By"] = "Wellness Companion AI"
        response.headers["X-API-Version"] = "1.0.0"
    
    def _is_origin_allowed(self, origin: Optional[str]) -> bool:
        """Check if origin is allowed"""
        if not origin:
            # Allow requests without origin (like Postman, curl)
            return True
        
        # Use the config's method
        return self.cors_config.is_origin_allowed(origin)


class TrustedHostMiddleware(BaseHTTPMiddleware):
    """Middleware to validate trusted hosts"""
    
    def __init__(
        self,
        app: FastAPI,
        trusted_hosts: Optional[List[str]] = None,
        www_redirect: bool = True
    ):
        super().__init__(app)
        self.trusted_hosts = trusted_hosts or get_security_config().trusted_hosts
        self.www_redirect = www_redirect
        
        # Compile patterns for wildcard hosts
        self.host_patterns = []
        for host in self.trusted_hosts:
            if "*" in host:
                # Convert wildcard to regex
                pattern = host.replace("*", r"[^.]+")
                pattern = pattern.replace(".", r"\.")
                self.host_patterns.append(re.compile(f"^{pattern}$"))
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Validate request host"""
        
        # Get host from headers
        host = request.headers.get("host", "")
        
        # Remove port from host for checking
        host_without_port = host.split(":")[0] if ":" in host else host
        
        # Check if host is trusted
        if not self._is_host_trusted(host_without_port):
            logger.warning(f"Untrusted host access attempt: {host}")
            return PlainTextResponse(
                "Invalid host header",
                status_code=400
            )
        
        return await call_next(request)
    
    def _is_host_trusted(self, host: str) -> bool:
        """Check if host is trusted"""
        # Direct match
        if host in self.trusted_hosts:
            return True
        
        # Pattern match for wildcards
        for pattern in self.host_patterns:
            if pattern.match(host):
                return True
        
        return False


def setup_cors_middleware(app: FastAPI) -> None:
    """Setup CORS middleware for FastAPI application"""
    
    cors_config = get_cors_config()
    security_config = get_security_config()
    
    # Add trusted host middleware first
    app.add_middleware(
        TrustedHostMiddleware,
        trusted_hosts=security_config.trusted_hosts
    )
    
    # Add enhanced CORS middleware
    app.add_middleware(
        EnhancedCORSMiddleware,
        cors_config=cors_config,
        security_config=security_config
    )
    
    # Log CORS configuration
    logger.info(f"CORS configured for environment: {cors_config.environment}")
    logger.info(f"Allowed origins: {len(cors_config.allowed_origins)} configured")
    logger.debug(f"CORS origins: {cors_config.allowed_origins}")
    
    if cors_config.allowed_origins_regex:
        logger.debug(f"CORS regex pattern: {cors_config.allowed_origins_regex}")
