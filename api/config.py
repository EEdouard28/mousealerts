"""
MouseAlerts API - Configuration Settings

This module defines all application settings using Pydantic BaseSettings.
It handles environment variable loading, type validation, and default values.

Key settings include:
- Database and Redis connection URLs
- JWT authentication configuration
- Notification service credentials (SendGrid, Twilio, Web Push)
- Stripe payment integration
- CORS and security settings

All settings can be overridden via environment variables or .env file.
"""

from pydantic_settings import BaseSettings
from pydantic import field_validator, model_validator, computed_field, Field
from typing import List, Union
import os

class Settings(BaseSettings):
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    APP_ENV: str = "dev"
    
    # Database
    DATABASE_URL: str = "sqlite:///./mousealerts.db"
    
    # Redis (disabled for local development)
    REDIS_URL: str = "redis://localhost:6379/0"
    USE_REDIS: bool = False
    
    # JWT
    JWT_SECRET: str = "changeme"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30
    
    @model_validator(mode='after')
    def validate_production_settings(self):
        """Ensure production settings are secure"""
        # Only validate if explicitly in production mode and JWT_SECRET is the default
        # Allow deployment to proceed if JWT_SECRET is set via environment variable
        if self.APP_ENV == 'production' and self.JWT_SECRET == 'changeme':
            # Check if JWT_SECRET was actually set via environment variable
            import os
            env_jwt_secret = os.getenv('JWT_SECRET', '')
            if not env_jwt_secret or env_jwt_secret == 'changeme':
                raise ValueError(
                    'JWT_SECRET must be changed from default value in production. '
                    'Generate one with: python3 -c "import secrets; print(secrets.token_urlsafe(32))"'
                )
        return self
    
    # CORS - Store as string to avoid JSON parsing issues, use Field alias for env var mapping
    allowed_origins_str: str = Field(
        default="http://localhost:3000,http://localhost:3001",
        alias="ALLOWED_ORIGINS"
    )
    allowed_hosts_str: str = Field(
        default="localhost,127.0.0.1",
        alias="ALLOWED_HOSTS"
    )
    
    @field_validator('allowed_origins_str', mode='before')
    @classmethod
    def parse_origins_input(cls, v):
        """Handle both string and list inputs for ALLOWED_ORIGINS"""
        if isinstance(v, list):
            return ','.join(str(item) for item in v)
        if isinstance(v, str):
            return v
        return "http://localhost:3000"
    
    @field_validator('allowed_hosts_str', mode='before')
    @classmethod
    def parse_hosts_input(cls, v):
        """Handle both string and list inputs for ALLOWED_HOSTS"""
        if isinstance(v, list):
            return ','.join(str(item) for item in v)
        if isinstance(v, str):
            return v
        return "localhost"
    
    @computed_field
    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        """Parse comma-separated origins string into list"""
        origins = [origin.strip() for origin in self.allowed_origins_str.split(',') if origin.strip()]
        return origins if origins else ["http://localhost:3000"]
    
    @computed_field
    @property
    def ALLOWED_HOSTS(self) -> List[str]:
        """Parse comma-separated hosts string into list"""
        hosts = [host.strip() for host in self.allowed_hosts_str.split(',') if host.strip()]
        return hosts if hosts else ["localhost"]
    
    # Notifications
    SENDGRID_API_KEY: str = ""
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_FROM_NUMBER: str = ""
    WEB_PUSH_VAPID_PUBLIC_KEY: str = ""
    WEB_PUSH_VAPID_PRIVATE_KEY: str = ""
    WEB_PUSH_VAPID_SUBJECT: str = "mailto:admin@mousealerts.app"
    
    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_PREMIUM: str = ""
    STRIPE_PRICE_FAMILY: str = ""
    
    # Monitoring
    SENTRY_DSN: str = ""
    
    # Magic Link
    MAGIC_LINK_EXPIRE_MINUTES: int = 15
    MAGIC_LINK_BASE_URL: str = "http://localhost:3000"
    
    # Scraper Configuration
    SCRAPER_PAGE_LOAD_TIMEOUT: int = 30
    SCRAPER_ELEMENT_WAIT_TIMEOUT: int = 10
    SCRAPER_IMPLICIT_WAIT: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        populate_by_name = True  # Allow both field name and alias

# Create global settings instance
settings = Settings()
