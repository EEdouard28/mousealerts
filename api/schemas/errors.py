"""
MouseAlerts API - Error Response Schemas

This module defines standardized error response formats for consistent API error handling.
All API errors should use these schemas for better frontend integration and debugging.
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any

class ErrorDetail(BaseModel):
    """Detailed error information"""
    message: str
    code: Optional[str] = None
    field: Optional[str] = None
    value: Optional[Any] = None

class ErrorResponse(BaseModel):
    """Standardized error response format"""
    error: str
    detail: Optional[str] = None
    errors: Optional[list[ErrorDetail]] = None
    request_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Validation Error",
                "detail": "Invalid input data",
                "errors": [
                    {
                        "message": "Field is required",
                        "code": "MISSING_FIELD",
                        "field": "venue",
                        "value": None
                    }
                ],
                "request_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }

