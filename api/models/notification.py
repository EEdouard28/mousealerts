"""
MouseAlerts API - Notification Model

This SQLAlchemy model tracks individual notifications sent to users.
Each notification represents one delivery attempt (email, SMS, or push).

Fields:
- id: Unique identifier (UUID)
- alert_id: Foreign key to Alert model
- channel: Notification channel (push, email, sms)
- status: Delivery status (pending, sent, failed)
- sent_at: Timestamp when notification was sent
- latency_ms: Time taken to send the notification

Relationships:
- alert: Many-to-one with Alert model

This model is used for tracking delivery success rates, debugging
notification issues, and analytics on notification performance.
"""

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db import Base

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(String, primary_key=True, index=True)
    alert_id = Column(String, ForeignKey("alerts.id"), nullable=False)
    channel = Column(String, nullable=False)  # push, email, sms
    status = Column(String, default="pending")  # pending, sent, failed
    sent_at = Column(DateTime(timezone=True))
    latency_ms = Column(Integer)
    
    # Relationships
    alert = relationship("Alert", back_populates="notifications")
