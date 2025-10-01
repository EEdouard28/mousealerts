"""
MouseAlerts API - Alert Model

This SQLAlchemy model represents dining reservation alerts created by users.
Each alert specifies what the user is looking for (venue, date, time, party size).

Fields:
- id: Unique identifier (UUID)
- user_id: Foreign key to User model
- park: Disney park (Magic Kingdom, EPCOT, etc.)
- venue: Restaurant name
- date: Reservation date
- time_start/time_end: Time window for reservation
- party_size: Number of people
- status: active, paused, or expired
- channels: JSON object with notification preferences (push, email, sms)
- created_at: Alert creation timestamp

Relationships:
- user: Many-to-one with User model
- notifications: One-to-many with Notification model
"""

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db import Base

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    park = Column(String, nullable=False)
    restaurant = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    time_start = Column(String, nullable=False)
    time_end = Column(String, nullable=False)
    party_size = Column(Integer, nullable=False)
    status = Column(String, default="active")  # active, paused, expired
    channels = Column(JSON)  # push, email, sms preferences
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="alerts")
    notifications = relationship("Notification", back_populates="alert")
