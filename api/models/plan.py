"""
MouseAlerts API - Plan Model

This SQLAlchemy model defines subscription plans available to users.
Plans control what features users can access and their limits.

Fields:
- id: Unique identifier (UUID)
- name: Plan name (free, premium, family)
- limits: JSON object containing plan limits and features
- price_cents: Monthly price in cents (0 for free plan)

Example limits JSON:
{
  "alerts_per_user": 2,
  "notification_channels": ["email"],
  "instant_notifications": false,
  "ai_prompt_bar": false
}

Relationships:
- subscriptions: One-to-many with Subscription model
"""

from sqlalchemy import Column, String, Integer, JSON
from sqlalchemy.orm import relationship
from db import Base

class Plan(Base):
    __tablename__ = "plans"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    limits = Column(JSON)  # alerts_per_user, notification_channels, etc.
    price_cents = Column(Integer, default=0)
    
    # Relationships
    subscriptions = relationship("Subscription", back_populates="plan")
