
# ========================================
# services/core-backend/src/core/security_config.py
# ========================================

"""
Security Configuration - Security headers and policies
Configures security-related settings for the application
"""

import os
from typing import Dict, List, Optional
from pydantic import BaseSettings, validator


class SecurityConfig(BaseSettings):
    """Security configuration settings"""
    
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    # Content Security Policy
    content_security_policy: Optional[str] = None
    
    # HTTP Security Headers
    security_headers: Dict[str, str] = {}
    
    # Trusted hosts
    trusted_hosts: List[str] = ["localhost", "127.0.0.1", "::1"]
    
    # HTTPS settings
    force_https: bool = False
    hsts_max_age: int = 31536000  # 1 year
    hsts_include_subdomains: bool = True
    hsts_preload: bool = False
    
    # Frame options
    x_frame_options: str = "DENY"
    
    # Content type options
    x_content_type_options: str = "nosniff"
    
    # XSS protection
    x_xss_protection: str = "1; mode=block"
    
    # Referrer policy
    referrer_policy: str = "strict-origin-when-cross-origin"
    
    # Permissions policy
    permissions_policy: Optional[str] = None
    
    @validator("security_headers", pre=True, always=True)
    def set_security_headers(cls, v, values):
        """Set security headers based on environment"""
        environment = values.get("environment", "development").lower()
        force_https = values.get("force_https", False)
        
        headers = {}
        
        # X-Frame-Options
        headers["X-Frame-Options"] = values.get("x_frame_options", "DENY")
        
        # X-Content-Type-Options
        headers["X-Content-Type-Options"] = values.get("x_content_type_options", "nosniff")
        
        # X-XSS-Protection
        headers["X-XSS-Protection"] = values.get("x_xss_protection", "1; mode=block")
        
        # Referrer-Policy
        headers["Referrer-Policy"] = values.get("referrer_policy", "strict-origin-when-cross-origin")
        
        # HSTS (only if HTTPS is forced)
        if force_https or environment == "production":
            hsts_max_age = values.get("hsts_max_age", 31536000)
            hsts_include_subdomains = values.get("hsts_include_subdomains", True)
            hsts_preload = values.get("hsts_preload", False)
            
            hsts_value = f"max-age={hsts_max_age}"
            if hsts_include_subdomains:
                hsts_value += "; includeSubDomains"
            if hsts_preload:
                hsts_value += "; preload"
            
            headers["Strict-Transport-Security"] = hsts_value
        
        # Content Security Policy
        if environment == "production":
            # Strict CSP for production
            csp = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "img-src 'self' data: https:; "
                "font-src 'self' https://cdn.jsdelivr.net; "
                "connect-src 'self' https: wss:; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            )
            headers["Content-Security-Policy"] = csp
        elif environment == "development":
            # Relaxed CSP for development
            csp = (
                "default-src 'self' 'unsafe-inline' 'unsafe-eval' *; "
                "img-src 'self' data: *; "
                "connect-src 'self' ws: wss: *"
            )
            headers["Content-Security-Policy"] = csp
        
        # Permissions Policy (formerly Feature Policy)
        permissions_policy = values.get("permissions_policy")
        if not permissions_policy and environment == "production":
            # Restrictive permissions policy for production
            permissions_policy = (
                "accelerometer=(), camera=(), geolocation=(), "
                "gyroscope=(), magnetometer=(), microphone=(), "
                "payment=(), usb=()"
            )
        
        if permissions_policy:
            headers["Permissions-Policy"] = permissions_policy
        
        # Custom headers from environment
        custom_headers = os.getenv("SECURITY_HEADERS", "")
        if custom_headers:
            try:
                for header_pair in custom_headers.split(";"):
                    if ":" in header_pair:
                        key, value = header_pair.split(":", 1)
                        headers[key.strip()] = value.strip()
            except Exception:
                pass  # Ignore malformed custom headers
        
        return headers
    
    @validator("trusted_hosts", pre=True, always=True)
    def set_trusted_hosts(cls, v, values):
        """Set trusted hosts based on environment"""
        environment = values.get("environment", "development").lower()
        
        hosts = ["localhost", "127.0.0.1", "::1"]
        
        if environment == "development":
            # Add common development hosts
            hosts.extend([
                "localhost:*",
                "127.0.0.1:*",
                "::1:*"
            ])
        
        # Add custom trusted hosts from environment
        custom_hosts = os.getenv("TRUSTED_HOSTS", "").split(",")
        custom_hosts = [host.strip() for host in custom_hosts if host.strip()]
        hosts.extend(custom_hosts)
        
        return list(set(hosts))  # Remove duplicates
    
    @validator("force_https", pre=True, always=True)
    def set_force_https(cls, v, values):
        """Set HTTPS enforcement based on environment"""
        environment = values.get("environment", "development").lower()
        
        # Force HTTPS in production unless explicitly disabled
        if environment == "production":
            return os.getenv("FORCE_HTTPS", "true").lower() == "true"
        
        # Allow HTTP in development unless explicitly enabled
        return os.getenv("FORCE_HTTPS", "false").lower() == "true"
    
    def get_security_middleware_kwargs(self) -> dict:
        """Get kwargs for security middleware"""
        return {
            "force_https": self.force_https,
            "trusted_hosts": self.trusted_hosts
        }
    
    class Config:
        env_prefix = "SECURITY_"
        case_sensitive = False


# Global security configuration instance
security_config = SecurityConfig()


def get_security_config() -> SecurityConfig:
    """Get the global security configuration"""
    return security_config

