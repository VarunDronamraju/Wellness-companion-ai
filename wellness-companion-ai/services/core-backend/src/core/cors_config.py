# ========================================
# services/core-backend/src/core/cors_config.py - FIXED
# ========================================

"""
CORS Configuration - Cross-Origin Resource Sharing settings
Configures CORS for desktop app communication and web access
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class CORSConfig(BaseSettings):
    """CORS configuration settings"""
    
    model_config = SettingsConfigDict(env_prefix="CORS_", case_sensitive=False)
    
    # Environment-based CORS settings
    environment: str = "development"
    
    # Allowed origins
    allowed_origins: List[str] = []
    allowed_origins_regex: Optional[str] = None
    
    # Allowed methods
    allowed_methods: List[str] = [
        "GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"
    ]
    
    # Allowed headers
    allowed_headers: List[str] = [
        "Accept", "Accept-Language", "Content-Language", "Content-Type",
        "Authorization", "X-Requested-With", "X-Request-ID", "X-API-Key",
        "X-User-ID", "X-Device-ID", "X-App-Version", "User-Agent",
        "Origin", "Cache-Control", "Pragma"
    ]
    
    # Exposed headers
    exposed_headers: List[str] = [
        "X-Request-ID", "X-Processing-Time", "X-Rate-Limit-Remaining",
        "X-Rate-Limit-Reset", "Content-Length", "Content-Range"
    ]
    
    # CORS options
    allow_credentials: bool = True
    max_age: int = 86400
    
    @field_validator("allowed_origins", mode="before")
    @classmethod
    def set_allowed_origins(cls, v, info):
        """Set allowed origins based on environment"""
        environment = os.getenv("ENVIRONMENT", "development").lower()
        
        # Base origins
        origins = [
            "app://localhost", "file://", "capacitor://localhost",
            "ionic://localhost", "http://localhost", "https://localhost",
            "http://127.0.0.1", "https://127.0.0.1"
        ]
        
        if environment == "development":
            # Development origins
            origins.extend([
                "http://localhost:3000", "http://localhost:3001",
                "http://localhost:5173", "http://localhost:8080",
                "http://localhost:4200", "http://127.0.0.1:3000",
                "http://127.0.0.1:5173", "http://127.0.0.1:8080"
            ])
        elif environment == "production":
            # Production origins from environment
            production_origins = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
            origins.extend([origin.strip() for origin in production_origins if origin.strip()])
        
        return list(set(origins))  # Remove duplicates
    
    @field_validator("allowed_origins_regex", mode="before")
    @classmethod
    def set_origins_regex(cls, v, info):
        """Set regex pattern for development"""
        environment = os.getenv("ENVIRONMENT", "development").lower()
        if environment == "development":
            return r"^https?://(localhost|127\.0\.0\.1|::1)(:\d+)?$"
        return v
    
    def __init__(self, **kwargs):
        # Set environment from OS env if not provided
        if "environment" not in kwargs:
            kwargs["environment"] = os.getenv("ENVIRONMENT", "development")
        super().__init__(**kwargs)
    
    def is_origin_allowed(self, origin: str) -> bool:
        """Check if an origin is allowed"""
        if origin in self.allowed_origins:
            return True
        
        if self.allowed_origins_regex:
            import re
            if re.match(self.allowed_origins_regex, origin):
                return True
        
        return False
    
    def get_cors_middleware_kwargs(self) -> dict:
        """Get kwargs for FastAPI CORSMiddleware"""
        return {
            "allow_origins": self.allowed_origins,
            "allow_origin_regex": self.allowed_origins_regex,
            "allow_credentials": self.allow_credentials,
            "allow_methods": self.allowed_methods,
            "allow_headers": self.allowed_headers,
            "expose_headers": self.exposed_headers,
            "max_age": self.max_age
        }


# Global instance
cors_config = CORSConfig()

def get_cors_config() -> CORSConfig:
    """Get the global CORS configuration"""
    return cors_config


# ========================================
# services/core-backend/src/core/security_config.py - FIXED
# ========================================

"""
Security Configuration - Security headers and policies
"""

import os
from typing import Dict, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class SecurityConfig(BaseSettings):
    """Security configuration settings"""
    
    model_config = SettingsConfigDict(env_prefix="SECURITY_", case_sensitive=False)
    
    environment: str = "development"
    security_headers: Dict[str, str] = {}
    trusted_hosts: List[str] = ["localhost", "127.0.0.1", "::1"]
    force_https: bool = False
    
    @field_validator("security_headers", mode="before")
    @classmethod
    def set_security_headers(cls, v, info):
        """Set security headers based on environment"""
        environment = os.getenv("ENVIRONMENT", "development").lower()
        
        headers = {
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }
        
        if environment == "production":
            headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            headers["Content-Security-Policy"] = (
                "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "img-src 'self' data: https:; connect-src 'self' https: wss:;"
            )
        
        return headers
    
    @field_validator("trusted_hosts", mode="before")
    @classmethod
    def set_trusted_hosts(cls, v, info):
        """Set trusted hosts"""
        hosts = ["localhost", "127.0.0.1", "::1"]
        custom_hosts = os.getenv("TRUSTED_HOSTS", "").split(",")
        hosts.extend([host.strip() for host in custom_hosts if host.strip()])
        return list(set(hosts))
    
    def __init__(self, **kwargs):
        if "environment" not in kwargs:
            kwargs["environment"] = os.getenv("ENVIRONMENT", "development")
        super().__init__(**kwargs)


# Global instance
security_config = SecurityConfig()

def get_security_config() -> SecurityConfig:
    """Get the global security configuration"""
    return security_config


# ========================================
# services/core-backend/src/api/middleware/cors_handler.py - SIMPLIFIED
# ========================================

"""
Enhanced CORS Handler - Simplified version without complex middleware
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from src.core.cors_config import get_cors_config
from src.core.security_config import get_security_config

logger = logging.getLogger(__name__)


def setup_cors_middleware(app: FastAPI) -> None:
    """Setup CORS middleware for FastAPI application"""
    
    cors_config = get_cors_config()
    security_config = get_security_config()
    
    # Add trusted host middleware
    if security_config.trusted_hosts:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=security_config.trusted_hosts
        )
    
    # Add standard CORS middleware with our configuration
    app.add_middleware(
        CORSMiddleware,
        **cors_config.get_cors_middleware_kwargs()
    )
    
    # Add a simple middleware to add security headers
    @app.middleware("http")
    async def add_security_headers(request, call_next):
        response = await call_next(request)
        
        # Add security headers
        for header_name, header_value in security_config.security_headers.items():
            response.headers[header_name] = header_value
        
        # Add custom headers
        response.headers["X-Powered-By"] = "Wellness Companion AI"
        response.headers["X-API-Version"] = "1.0.0"
        
        return response
    
    logger.info(f"CORS configured for environment: {cors_config.environment}")
    logger.info(f"Allowed origins: {len(cors_config.allowed_origins)} configured")
    logger.info("Security headers configured")