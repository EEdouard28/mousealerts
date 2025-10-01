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
from typing import List
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
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    
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
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create global settings instance
settings = Settings()
