"""
MouseAlerts API - Admin Configuration

This module handles admin-specific configuration and security settings.
It provides environment-based admin access control and security features.

Environment Variables:
- ADMIN_EMAILS: Comma-separated list of admin emails
- ADMIN_USER_IDS: Comma-separated list of admin user IDs
- ADMIN_SECRET_KEY: Secret key for admin operations
- ADMIN_IP_WHITELIST: Comma-separated list of allowed IPs (optional)
- ADMIN_SESSION_TIMEOUT: Admin session timeout in minutes
"""

import os
from typing import List, Optional
from config import settings

class AdminConfig:
    """Admin configuration and security settings"""
    
    # Admin access control
    ADMIN_EMAILS: List[str] = os.getenv("ADMIN_EMAILS", "admin@mousealerts.com").split(",")
    ADMIN_USER_IDS: List[str] = os.getenv("ADMIN_USER_IDS", "").split(",") if os.getenv("ADMIN_USER_IDS") else []
    ADMIN_SECRET_KEY: str = os.getenv("ADMIN_SECRET_KEY", "admin-secret-key-change-in-production")
    
    # Security settings
    ADMIN_IP_WHITELIST: List[str] = os.getenv("ADMIN_IP_WHITELIST", "").split(",") if os.getenv("ADMIN_IP_WHITELIST") else []
    ADMIN_SESSION_TIMEOUT: int = int(os.getenv("ADMIN_SESSION_TIMEOUT", "60"))  # minutes
    
    # Admin dashboard settings
    ADMIN_REFRESH_INTERVAL: int = int(os.getenv("ADMIN_REFRESH_INTERVAL", "30"))  # seconds
    ADMIN_LOG_RETENTION_DAYS: int = int(os.getenv("ADMIN_LOG_RETENTION_DAYS", "30"))
    
    # Security features
    ADMIN_2FA_REQUIRED: bool = os.getenv("ADMIN_2FA_REQUIRED", "false").lower() == "true"
    ADMIN_AUDIT_LOGGING: bool = os.getenv("ADMIN_AUDIT_LOGGING", "true").lower() == "true"
    
    @classmethod
    def is_admin_email(cls, email: str) -> bool:
        """Check if email is in admin list"""
        return email in cls.ADMIN_EMAILS
    
    @classmethod
    def is_admin_user_id(cls, user_id: str) -> bool:
        """Check if user ID is in admin list"""
        return user_id in cls.ADMIN_USER_IDS
    
    @classmethod
    def is_admin_ip(cls, ip: str) -> bool:
        """Check if IP is whitelisted (if whitelist is configured)"""
        if not cls.ADMIN_IP_WHITELIST or not cls.ADMIN_IP_WHITELIST[0]:
            return True  # No whitelist configured
        return ip in cls.ADMIN_IP_WHITELIST
    
    @classmethod
    def get_admin_config(cls) -> dict:
        """Get admin configuration for frontend"""
        return {
            "refreshInterval": cls.ADMIN_REFRESH_INTERVAL,
            "sessionTimeout": cls.ADMIN_SESSION_TIMEOUT,
            "auditLogging": cls.ADMIN_AUDIT_LOGGING,
            "twoFactorRequired": cls.ADMIN_2FA_REQUIRED
        }

# Create admin config instance
admin_config = AdminConfig()
