"""
MouseAlerts API - WatcherRun Model

This SQLAlchemy model tracks background worker runs that check for availability.
Each run represents a single check of a venue for available reservation slots.

Fields:
- id: Unique identifier (UUID)
- venue: Restaurant name being checked
- run_at: Timestamp when the check was performed
- result_json: JSON data containing found availability slots
- found_count: Number of available slots found
- error: Error message if the check failed

This model is used for monitoring, debugging, and analytics of the background
worker system that polls Disney's reservation system.
"""

from sqlalchemy import Column, String, DateTime, Integer, JSON
from sqlalchemy.sql import func
from db import Base

class WatcherRun(Base):
    __tablename__ = "watcher_runs"
    
    id = Column(String, primary_key=True, index=True)
    venue = Column(String, nullable=False)
    run_at = Column(DateTime(timezone=True), server_default=func.now())
    result_json = Column(JSON)
    found_count = Column(Integer, default=0)
    error = Column(String)
