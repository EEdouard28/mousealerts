"""
MouseAlerts API - Admin Service

This service handles admin role management and permissions.
It provides secure access control for admin dashboard features.

Features:
- Admin role verification
- Permission checking
- Admin user management
- Security logging
"""

from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from models.user import User
from models.admin import Admin
import logging

logger = logging.getLogger(__name__)

class AdminService:
    """Service for managing admin roles and permissions"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def is_admin(self, user_id: str) -> bool:
        """Check if user is an admin"""
        admin = self.db.query(Admin).filter(
            Admin.user_id == user_id,
            Admin.is_active == True
        ).first()
        return admin is not None
    
    def get_admin_role(self, user_id: str) -> Optional[str]:
        """Get admin role for user"""
        admin = self.db.query(Admin).filter(
            Admin.user_id == user_id,
            Admin.is_active == True
        ).first()
        return admin.role if admin else None
    
    def has_permission(self, user_id: str, permission: str) -> bool:
        """Check if admin has specific permission"""
        admin = self.db.query(Admin).filter(
            Admin.user_id == user_id,
            Admin.is_active == True
        ).first()
        
        if not admin:
            return False
        
        return admin.has_permission(permission)
    
    def can_access_admin(self, user_id: str) -> bool:
        """Check if user can access admin dashboard"""
        return self.is_admin(user_id)
    
    def can_manage_users(self, user_id: str) -> bool:
        """Check if admin can manage users"""
        return self.has_permission(user_id, "user_management")
    
    def can_monitor_system(self, user_id: str) -> bool:
        """Check if admin can monitor system"""
        return self.has_permission(user_id, "system_monitoring")
    
    def can_access_billing(self, user_id: str) -> bool:
        """Check if admin can access billing data"""
        return self.has_permission(user_id, "billing_access")
    
    def can_manage_admins(self, user_id: str) -> bool:
        """Check if admin can manage other admins"""
        admin = self.db.query(Admin).filter(
            Admin.user_id == user_id,
            Admin.is_active == True
        ).first()
        
        if not admin:
            return False
        
        return admin.can_manage_admins()
    
    def get_admin_info(self, user_id: str) -> Optional[Dict]:
        """Get admin information for user"""
        admin = self.db.query(Admin).filter(
            Admin.user_id == user_id,
            Admin.is_active == True
        ).first()
        
        if not admin:
            return None
        
        return {
            "id": admin.id,
            "role": admin.role,
            "permissions": admin.permissions,
            "created_at": admin.created_at,
            "last_login": admin.last_login,
            "is_active": admin.is_active
        }
    
    def create_admin(self, user_id: str, role: str = "admin", permissions: Dict = None) -> Admin:
        """Create admin access for user"""
        try:
            # Check if user exists
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.error(f"User {user_id} not found for admin creation")
                raise ValueError(f"User with ID {user_id} not found")
            
            # Check if already admin
            existing_admin = self.db.query(Admin).filter(Admin.user_id == user_id).first()
            if existing_admin:
                logger.warning(f"User {user_id} already has admin access")
                raise ValueError(f"User {user_id} is already an admin")
            
            # Create admin record
            admin = Admin(
                user_id=user_id,
                role=role,
                permissions=permissions or {
                    "user_management": True,
                    "system_monitoring": True,
                    "billing_access": True,
                    "admin_management": role == "super_admin"
                }
            )
            
            self.db.add(admin)
            self.db.commit()
            
            logger.info(f"Admin access created for user {user_id} with role {role}")
            return admin
            
        except Exception as e:
            logger.error(f"Failed to create admin for user {user_id}: {str(e)}")
            self.db.rollback()
            raise
    
    def update_admin_permissions(self, user_id: str, permissions: Dict) -> bool:
        """Update admin permissions"""
        try:
            admin = self.db.query(Admin).filter(
                Admin.user_id == user_id,
                Admin.is_active == True
            ).first()
            
            if not admin:
                logger.error(f"Admin {user_id} not found for permission update")
                return False
            
            admin.permissions = permissions
            self.db.commit()
            
            logger.info(f"Admin permissions updated for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update admin permissions for user {user_id}: {str(e)}")
            self.db.rollback()
            return False
    
    def deactivate_admin(self, user_id: str) -> bool:
        """Deactivate admin access"""
        try:
            admin = self.db.query(Admin).filter(Admin.user_id == user_id).first()
            
            if not admin:
                logger.error(f"Admin {user_id} not found for deactivation")
                return False
            
            admin.is_active = False
            self.db.commit()
            
            logger.info(f"Admin access deactivated for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deactivate admin for user {user_id}: {str(e)}")
            self.db.rollback()
            return False
    
    def get_all_admins(self) -> List[Dict]:
        """Get all admin users"""
        admins = self.db.query(Admin, User).join(User).filter(Admin.is_active == True).all()
        
        return [
            {
                "id": admin.id,
                "user_id": admin.user_id,
                "email": user.email,
                "phone": user.phone,
                "role": admin.role,
                "permissions": admin.permissions,
                "created_at": admin.created_at,
                "last_login": admin.last_login
            }
            for admin, user in admins
        ]
    
    def is_super_admin(self, user_id: str) -> bool:
        """Check if user is a super admin"""
        admin = self.db.query(Admin).filter(
            Admin.user_id == user_id,
            Admin.is_active == True
        ).first()
        return admin and admin.role == "super_admin"
    
    def update_admin_role(self, user_id: str, role: str) -> Admin:
        """Update admin role"""
        try:
            admin = self.db.query(Admin).filter(
                Admin.user_id == user_id,
                Admin.is_active == True
            ).first()
            
            if not admin:
                raise ValueError(f"Admin {user_id} not found")
            
            admin.role = role
            # Update permissions based on role
            admin.permissions["admin_management"] = role == "super_admin"
            self.db.commit()
            
            logger.info(f"Admin role updated for user {user_id} to {role}")
            return admin
            
        except Exception as e:
            logger.error(f"Failed to update admin role for user {user_id}: {str(e)}")
            self.db.rollback()
            raise
    
    def delete_admin(self, user_id: str) -> bool:
        """Delete admin access"""
        try:
            admin = self.db.query(Admin).filter(Admin.user_id == user_id).first()
            
            if not admin:
                logger.error(f"Admin {user_id} not found for deletion")
                return False
            
            self.db.delete(admin)
            self.db.commit()
            
            logger.info(f"Admin access deleted for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete admin for user {user_id}: {str(e)}")
            self.db.rollback()
            return False
    
    def log_admin_action(self, user_id: str, action: str, details: str = None):
        """Log admin action for security auditing"""
        logger.info(f"Admin action: User {user_id} performed {action}" + 
                   (f" - {details}" if details else ""))
