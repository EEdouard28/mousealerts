"""
MouseAlerts API - Admin Model

This SQLAlchemy model defines admin users and their roles.
Admins have elevated permissions to access admin dashboard,
user management, and system monitoring.

Fields:
- id: Unique identifier (UUID)
- user_id: Reference to User model
- role: Admin role (super_admin, admin, moderator)
- permissions: JSON object containing specific permissions
- created_at: When admin access was granted
- last_login: Last admin login timestamp
- is_active: Whether admin access is active

Admin Roles:
- super_admin: Full system access, can manage other admins
- admin: Standard admin access, user management, system monitoring
- moderator: Limited access, user support, basic monitoring

Permissions JSON:
{
  "user_management": true,
  "system_monitoring": true,
  "billing_access": true,
  "admin_management": false
}
"""

from sqlalchemy import Column, String, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db import Base
import uuid

class Admin(Base):
    __tablename__ = "admins"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True)
    role = Column(String, nullable=False, default="admin")  # super_admin, admin, moderator
    permissions = Column(JSON, default=lambda: {
        "user_management": True,
        "system_monitoring": True,
        "billing_access": True,
        "admin_management": False
    })
    created_at = Column(DateTime, default=func.now())
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="admin_profile")
    
    def has_permission(self, permission: str) -> bool:
        """Check if admin has specific permission"""
        return self.permissions.get(permission, False)
    
    def is_super_admin(self) -> bool:
        """Check if admin is super admin"""
        return self.role == "super_admin"
    
    def can_manage_admins(self) -> bool:
        """Check if admin can manage other admins"""
        return self.is_super_admin() or self.has_permission("admin_management")
