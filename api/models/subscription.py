"""
MouseAlerts API - Subscription Model

This SQLAlchemy model tracks user subscriptions to paid plans.
Subscriptions are managed via Stripe webhooks and control user access.

Fields:
- id: Unique identifier (UUID)
- user_id: Foreign key to User model
- plan_id: Foreign key to Plan model
- status: Subscription status (active, cancelled, past_due)
- current_period_end: When the current billing period ends
- created_at: Subscription creation timestamp

Relationships:
- user: Many-to-one with User model
- plan: Many-to-one with Plan model

This model is updated via Stripe webhooks when users subscribe,
cancel, or update their plans.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db import Base

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    plan_id = Column(String, ForeignKey("plans.id"), nullable=False)
    status = Column(String, default="active")  # active, cancelled, past_due
    current_period_end = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    plan = relationship("Plan", back_populates="subscriptions")
