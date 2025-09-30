"""
MouseAlerts API - Alert Pydantic Schemas

This module defines Pydantic schemas for alert-related API requests and responses.
These schemas handle data validation for Disney dining reservation alerts.

Schemas:
- AlertBase: Common alert fields
- AlertCreate: Data for creating new alerts
- AlertUpdate: Data for updating existing alerts
- AlertResponse: Alert data returned by API

These schemas ensure proper validation of park names, venue names,
date/time formats, and party sizes.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class AlertBase(BaseModel):
    park: str
    venue: str
    date: datetime
    time_start: str
    time_end: str
    party_size: int
    channels: Optional[Dict[str, Any]] = None

class AlertCreate(AlertBase):
    pass

class AlertUpdate(BaseModel):
    park: Optional[str] = None
    venue: Optional[str] = None
    date: Optional[datetime] = None
    time_start: Optional[str] = None
    time_end: Optional[str] = None
    party_size: Optional[int] = None
    status: Optional[str] = None
    channels: Optional[Dict[str, Any]] = None

class AlertResponse(AlertBase):
    id: str
    user_id: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True
