# ========================================
# services/core-backend/src/core/settings.py - COMPLETE FIX
# ========================================

"""
Core Backend Settings - Wellness Companion AI
Environment-based configuration with validation
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional
import os


class CoreBackendSettings(BaseSettings):
    """Core Backend service configuration"""
    
    # === SERVICE CONFIGURATION ===
    service_name: str = "core-backend"
    version: str = "1.0.0"
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    
    # === NETWORK CONFIGURATION ===
    host: str = Field(default="0.0.0.0", env="CORE_BACKEND_HOST")
    port: int = Field(default=8001, env="CORE_BACKEND_PORT")
    
    # === SECURITY CONFIGURATION === 
    # FIXED: Use string with default values that work
    cors_origins: str = Field(default="*", env="CORS_ORIGINS")
    cors_methods: str = Field(default="GET,POST,PUT,DELETE,OPTIONS", env="CORS_METHODS")
    cors_credentials: bool = Field(default=True, env="CORS_CREDENTIALS")
    
    # === EXTERNAL SERVICES ===
    aiml_service_url: str = Field(
        default="http://aiml-orchestration:8000", 
        env="AIML_SERVICE_URL"
    )
    data_layer_url: str = Field(
        default="http://data-layer:8000", 
        env="DATA_LAYER_URL"
    )
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")
    
    # === AUTHENTICATION (Phase 6) ===
    jwt_secret_key: Optional[str] = Field(default=None, env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # === OAUTH PROVIDERS (Phase 6) ===
    google_client_id: Optional[str] = Field(default=None, env="GOOGLE_CLIENT_ID")
    google_client_secret: Optional[str] = Field(default=None, env="GOOGLE_CLIENT_SECRET")
    aws_cognito_user_pool_id: Optional[str] = Field(default=None, env="AWS_COGNITO_USER_POOL_ID")
    
    # === API CONFIGURATION ===
    api_v1_prefix: str = "/api"
    max_upload_size: int = Field(default=10485760, env="MAX_UPLOAD_SIZE")  # 10MB
    
    # === FILE CONFIGURATION ===
    # FIXED: Use string instead of List
    allowed_file_types: str = Field(default="pdf,docx,txt,md", env="ALLOWED_FILE_TYPES")
    
    # === LOGGING ===
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    @validator('environment')
    def validate_environment(cls, v):
        """Validate environment values"""
        allowed = ['development', 'staging', 'production']
        if v.lower() not in allowed:
            raise ValueError(f'Environment must be one of: {allowed}')
        return v.lower()
    
    # === HELPER PROPERTIES ===
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as list"""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(',') if origin.strip()]
    
    @property
    def cors_methods_list(self) -> List[str]:
        """Get CORS methods as list"""
        return [method.strip() for method in self.cors_methods.split(',') if method.strip()]
    
    @property
    def allowed_file_types_list(self) -> List[str]:
        """Get allowed file types as list"""
        return [file_type.strip() for file_type in self.allowed_file_types.split(',') if file_type.strip()]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance with error handling
try:
    settings = CoreBackendSettings()
    print(f"✅ Settings loaded successfully: {settings.service_name} v{settings.version}")
    print(f"📍 Environment: {settings.environment}")
    print(f"🌐 CORS Origins: {settings.cors_origins_list}")
    print(f"📁 File Types: {settings.allowed_file_types_list}")
except Exception as e:
    print(f"❌ Failed to load settings: {e}")
    # Create minimal fallback settings
    settings = CoreBackendSettings(
        cors_origins="*",
        cors_methods="GET,POST,PUT,DELETE,OPTIONS",
        allowed_file_types="pdf,docx,txt,md"
    )
    print("🔄 Using fallback settings")