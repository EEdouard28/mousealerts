"""
MouseAlerts API - User Pydantic Schemas

This module defines Pydantic schemas for user-related API requests and responses.
These schemas handle data validation, serialization, and documentation.

Schemas:
- UserBase: Common user fields
- UserCreate: Data for creating new users
- UserResponse: User data returned by API
- UserUpdate: Data for updating user information

These schemas ensure type safety and automatic API documentation generation.
"""

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: str
    created_at: datetime
    is_active: bool
    plan: str
    subscription_status: str
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    is_active: Optional[bool] = None
    plan: Optional[str] = None
    subscription_status: Optional[str] = None
