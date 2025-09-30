"""
MouseAlerts API - User Model

This SQLAlchemy model represents users in the system.
Users are created via magic link authentication and can have multiple alerts.

Fields:
- id: Unique identifier (UUID)
- email: User's email address (unique, indexed)
- created_at: Account creation timestamp
- is_active: Whether account is active/enabled
- plan: Current subscription plan (free, premium, family)
- subscription_status: Stripe subscription status

Relationships:
- alerts: One-to-many with Alert model
- subscriptions: One-to-many with Subscription model
"""

from sqlalchemy import Column, String, DateTime, Boolean, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    plan = Column(String, default="free")
    subscription_status = Column(String, default="inactive")
    
    # Relationships
    alerts = relationship("Alert", back_populates="user")
    subscriptions = relationship("Subscription", back_populates="user")
