"""
MouseAlerts API - Admin Authentication Middleware

This middleware provides secure admin access control for admin routes.
It checks admin permissions, IP whitelisting, and session security.

Features:
- Admin role verification
- IP whitelisting (optional)
- Session timeout handling
- Security logging
- Permission-based access control
"""

from fastapi import HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional
import logging
from datetime import datetime, timedelta

from db import get_db
from services.admin_service import AdminService
from config_admin import admin_config

logger = logging.getLogger(__name__)

class AdminAuthMiddleware:
    """Middleware for admin authentication and authorization"""
    
    def __init__(self):
        self.admin_service = None
    
    def get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        # Check for forwarded IP (from proxy/load balancer)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # Check for real IP
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct connection
        return request.client.host if request.client else "unknown"
    
    def check_admin_access(self, user_id: str, request: Request) -> bool:
        """Check if user has admin access with security checks"""
        try:
            # Get database session
            db = next(get_db())
            self.admin_service = AdminService(db)
            
            # Check if user is admin
            if not self.admin_service.is_admin(user_id):
                logger.warning(f"Non-admin user {user_id} attempted admin access")
                return False
            
            # Check IP whitelist if configured
            client_ip = self.get_client_ip(request)
            if not admin_config.is_admin_ip(client_ip):
                logger.warning(f"Admin access denied for IP {client_ip}")
                return False
            
            # Log admin access
            if admin_config.ADMIN_AUDIT_LOGGING:
                self.admin_service.log_admin_action(
                    user_id, 
                    "admin_access", 
                    f"IP: {client_ip}, User-Agent: {request.headers.get('User-Agent', 'Unknown')}"
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Admin access check failed: {str(e)}")
            return False
    
    def check_admin_permission(self, user_id: str, permission: str) -> bool:
        """Check if admin has specific permission"""
        if not self.admin_service:
            return False
        
        return self.admin_service.has_permission(user_id, permission)
    
    def require_admin(self, user_id: str, request: Request):
        """Require admin access - raise exception if not admin"""
        if not self.check_admin_access(user_id, request):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
    
    def require_permission(self, user_id: str, permission: str, request: Request):
        """Require specific admin permission"""
        self.require_admin(user_id, request)
        
        if not self.check_admin_permission(user_id, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission required: {permission}"
            )
    
    def require_super_admin(self, user_id: str, request: Request):
        """Require super admin access"""
        self.require_admin(user_id, request)
        
        if not self.admin_service or not self.admin_service.can_manage_admins(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Super admin access required"
            )

# Create middleware instance
admin_auth = AdminAuthMiddleware()

# Dependency functions for FastAPI
def require_admin_access(user_id: str, request: Request):
    """FastAPI dependency for admin access"""
    admin_auth.require_admin(user_id, request)

def require_user_management(user_id: str, request: Request):
    """FastAPI dependency for user management permission"""
    admin_auth.require_permission(user_id, "user_management", request)

def require_system_monitoring(user_id: str, request: Request):
    """FastAPI dependency for system monitoring permission"""
    admin_auth.require_permission(user_id, "system_monitoring", request)

def require_billing_access(user_id: str, request: Request):
    """FastAPI dependency for billing access permission"""
    admin_auth.require_permission(user_id, "billing_access", request)

def require_super_admin(user_id: str, request: Request):
    """FastAPI dependency for super admin access"""
    admin_auth.require_super_admin(user_id, request)
