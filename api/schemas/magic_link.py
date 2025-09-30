"""
Magic Link Schemas

Pydantic schemas for SMS magic link authentication endpoints.
"""

from pydantic import BaseModel, Field, validator
import re
from typing import Optional
from datetime import datetime


class MagicLinkRequest(BaseModel):
    """Request schema for magic link generation"""
    phone: str = Field(..., description="Phone number in E.164 format (e.g., +1234567890)")
    
    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number format"""
        # Remove any spaces or dashes
        phone = re.sub(r'[\s\-]', '', v)
        
        # Check E.164 format: + followed by 10-15 digits
        if not re.match(r'^\+\d{10,15}$', phone):
            raise ValueError('Phone number must be in E.164 format (e.g., +1234567890)')
        
        return phone


class MagicLinkResponse(BaseModel):
    """Response schema for magic link generation"""
    success: bool = Field(..., description="Whether the magic link was sent successfully")
    message: str = Field(..., description="Human-readable message")
    expires_in_minutes: int = Field(15, description="Token expiration time in minutes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Magic link sent to +1234567890",
                "expires_in_minutes": 15
            }
        }


class MagicLinkVerifyRequest(BaseModel):
    """Request schema for magic link verification"""
    token: str = Field(..., description="Magic link token from SMS")


class MagicLinkVerifyResponse(BaseModel):
    """Response schema for magic link verification"""
    success: bool = Field(..., description="Whether the token was valid")
    access_token: Optional[str] = Field(None, description="JWT access token if successful")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(3600, description="Access token expiration in seconds")
    user_id: Optional[str] = Field(None, description="User ID if successful")
    message: str = Field(..., description="Human-readable message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "message": "Login successful"
            }
        }


class RateLimitResponse(BaseModel):
    """Response schema for rate limiting"""
    is_rate_limited: bool = Field(..., description="Whether the phone is rate limited")
    tokens_used: int = Field(..., description="Number of tokens used in the last hour")
    max_tokens: int = Field(..., description="Maximum tokens allowed per hour")
    reset_time: datetime = Field(..., description="When the rate limit resets")
    
    class Config:
        json_schema_extra = {
            "example": {
                "is_rate_limited": False,
                "tokens_used": 2,
                "max_tokens": 5,
                "reset_time": "2024-01-01T12:00:00Z"
            }
        }


class ErrorResponse(BaseModel):
    """Error response schema"""
    success: bool = Field(False, description="Always false for errors")
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(None, description="Additional error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "RATE_LIMITED",
                "message": "Too many requests. Please try again later.",
                "details": {
                    "reset_time": "2024-01-01T12:00:00Z"
                }
            }
        }
