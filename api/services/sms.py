"""
SMS Service

Handles sending SMS messages via Twilio for magic link authentication.
Includes rate limiting, message templates, and error handling.
"""

import os
import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import Optional
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
from sqlalchemy.orm import Session
from models.magic_link_token import MagicLinkToken
from config import Settings

settings = Settings()

class SMSService:
    """Service for sending SMS messages via Twilio"""
    
    def __init__(self):
        try:
            self.client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
            self.from_number = settings.TWILIO_FROM_NUMBER
        except Exception:
            # For testing or when credentials are not available
            self.client = None
            self.from_number = "+1234567890"
    
    def generate_magic_link_token(self) -> str:
        """Generate a secure random token for magic link"""
        # Generate 32-character random token
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(32))
    
    def create_magic_link_token(
        self, 
        db: Session, 
        phone: str, 
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> MagicLinkToken:
        """Create a new magic link token in the database"""
        
        # Clean up expired tokens for this phone number
        self._cleanup_expired_tokens(db, phone)
        
        # Generate secure token
        token = self.generate_magic_link_token()
        
        # Set expiration to 15 minutes from now
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
        
        # Create token record
        magic_token = MagicLinkToken(
            phone=phone,
            token=token,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.add(magic_token)
        db.commit()
        db.refresh(magic_token)
        
        return magic_token
    
    def send_magic_link_sms(self, phone: str, token: str) -> bool:
        """Send magic link SMS via Twilio"""
        try:
            # If no client (testing mode), return True
            if self.client is None:
                return True
                
            # Construct magic link URL
            base_url = os.getenv("NEXT_PUBLIC_API_BASE", "http://localhost:3000")
            magic_link = f"{base_url}/auth/verify?token={token}"
            
            # SMS message template
            message = f"""Your MouseAlerts login link: {magic_link}
Expires in 15 minutes. Reply STOP to opt out."""
            
            # Send SMS via Twilio
            message_obj = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=phone
            )
            
            return message_obj.sid is not None
            
        except TwilioException as e:
            print(f"Twilio SMS error: {e}")
            return False
        except Exception as e:
            print(f"SMS sending error: {e}")
            return False
    
    def verify_magic_link_token(
        self, 
        db: Session, 
        token: str
    ) -> Optional[MagicLinkToken]:
        """Verify and mark magic link token as used"""
        
        # Find token in database
        magic_token = db.query(MagicLinkToken).filter(
            MagicLinkToken.token == token
        ).first()
        
        if not magic_token:
            return None
        
        # Check if token is valid (not expired and not used)
        if not magic_token.is_valid:
            return None
        
        # Mark token as used
        magic_token.used_at = datetime.now(timezone.utc)
        db.commit()
        
        return magic_token
    
    def _cleanup_expired_tokens(self, db: Session, phone: str):
        """Clean up expired tokens for a phone number"""
        expired_tokens = db.query(MagicLinkToken).filter(
            MagicLinkToken.phone == phone,
            MagicLinkToken.expires_at < datetime.now(timezone.utc)
        ).all()
        
        for token in expired_tokens:
            db.delete(token)
        
        db.commit()
    
    def get_rate_limit_status(self, db: Session, phone: str) -> dict:
        """Check rate limiting status for a phone number"""
        # Count tokens created in the last hour
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        
        recent_tokens = db.query(MagicLinkToken).filter(
            MagicLinkToken.phone == phone,
            MagicLinkToken.created_at >= one_hour_ago
        ).count()
        
        # Rate limit: max 5 tokens per hour per phone
        max_tokens_per_hour = 5
        is_rate_limited = recent_tokens >= max_tokens_per_hour
        
        return {
            "is_rate_limited": is_rate_limited,
            "tokens_used": recent_tokens,
            "max_tokens": max_tokens_per_hour,
            "reset_time": one_hour_ago + timedelta(hours=1)
        }
