# Schemas package
from .user import UserBase, UserCreate, UserResponse
from .alert import AlertBase, AlertCreate, AlertUpdate, AlertResponse
from .magic_link import (
    MagicLinkRequest,
    MagicLinkResponse,
    MagicLinkVerifyRequest,
    MagicLinkVerifyResponse,
    RateLimitResponse,
    ErrorResponse
)

__all__ = [
    "UserBase",
    "UserCreate", 
    "UserResponse",
    "AlertBase",
    "AlertCreate",
    "AlertUpdate",
    "AlertResponse",
    "MagicLinkRequest",
    "MagicLinkResponse",
    "MagicLinkVerifyRequest",
    "MagicLinkVerifyResponse",
    "RateLimitResponse",
    "ErrorResponse"
]
