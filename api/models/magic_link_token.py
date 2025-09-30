"""
Magic Link Token Model

This model stores SMS magic link tokens for passwordless authentication.
Each token is single-use and expires after 15 minutes for security.
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from db import Base


class MagicLinkToken(Base):
    __tablename__ = "magic_link_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone = Column(String(20), nullable=False, index=True)  # E.164 format: +1234567890
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Additional security fields
    ip_address = Column(String(45), nullable=True)  # Store IP for rate limiting
    user_agent = Column(Text, nullable=True)  # Store user agent for security
    
    def __repr__(self):
        return f"<MagicLinkToken(id={self.id}, phone={self.phone}, expires_at={self.expires_at})>"
    
    @property
    def is_expired(self):
        """Check if token is expired"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) > self.expires_at
    
    @property
    def is_used(self):
        """Check if token has been used"""
        return self.used_at is not None
    
    @property
    def is_valid(self):
        """Check if token is valid (not expired and not used)"""
        return not self.is_expired and not self.is_used
