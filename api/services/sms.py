"""
SMS Service

Handles sending SMS messages via Twilio for magic link authentication.
Includes rate limiting, message templates, and error handling.
"""

import os
import secrets
import string
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
from sqlalchemy.orm import Session
from models.magic_link_token import MagicLinkToken
from config import Settings

settings = Settings()
logger = logging.getLogger(__name__)

class SMSService:
    """Service for sending SMS messages via Twilio"""
    
    def __init__(self):
        # #region agent log
        import json
        try:
            with open('/Users/evmacbook/the_edouard_company/mousealerts/.cursor/debug.log', 'a') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"sms.py:__init__","message":"SMSService init start","data":{"has_account_sid":bool(settings.TWILIO_ACCOUNT_SID),"has_auth_token":bool(settings.TWILIO_AUTH_TOKEN),"has_from_number":bool(settings.TWILIO_FROM_NUMBER)},"timestamp":int(datetime.now().timestamp()*1000)})+'\n')
        except: pass
        # #endregion
        try:
            self.client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
            self.from_number = settings.TWILIO_FROM_NUMBER
            # #region agent log
            try:
                with open('/Users/evmacbook/the_edouard_company/mousealerts/.cursor/debug.log', 'a') as f:
                    f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"sms.py:__init__","message":"Twilio client initialized successfully","data":{"from_number":self.from_number},"timestamp":int(datetime.now().timestamp()*1000)})+'\n')
            except: pass
            # #endregion
        except Exception as e:
            # #region agent log
            try:
                with open('/Users/evmacbook/the_edouard_company/mousealerts/.cursor/debug.log', 'a') as f:
                    f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"sms.py:__init__","message":"Twilio client init failed","data":{"error_type":type(e).__name__,"error_msg":str(e)},"timestamp":int(datetime.now().timestamp()*1000)})+'\n')
            except: pass
            # #endregion
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
        # #region agent log
        import json
        try:
            with open('/Users/evmacbook/the_edouard_company/mousealerts/.cursor/debug.log', 'a') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B,C,D","location":"sms.py:send_magic_link_sms","message":"send_magic_link_sms called","data":{"phone":phone,"has_client":self.client is not None,"has_base_url":bool(settings.MAGIC_LINK_BASE_URL),"base_url":settings.MAGIC_LINK_BASE_URL},"timestamp":int(datetime.now().timestamp()*1000)})+'\n')
        except: pass
        # #endregion
        try:
            # If no client (testing mode), log and return True for demo purposes
            if self.client is None:
                logger.warning("Twilio client not initialized - SMS not sent (testing mode)")
                # #region agent log
                try:
                    with open('/Users/evmacbook/the_edouard_company/mousealerts/.cursor/debug.log', 'a') as f:
                        f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"sms.py:send_magic_link_sms","message":"Client is None, returning True","data":{},"timestamp":int(datetime.now().timestamp()*1000)})+'\n')
                except: pass
                # #endregion
                return True
                
            # Check if Twilio credentials are configured
            if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
                logger.warning("Twilio credentials not configured - SMS not sent")
                # #region agent log
                try:
                    with open('/Users/evmacbook/the_edouard_company/mousealerts/.cursor/debug.log', 'a') as f:
                        f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"sms.py:send_magic_link_sms","message":"Twilio credentials not configured","data":{},"timestamp":int(datetime.now().timestamp()*1000)})+'\n')
                except: pass
                # #endregion
                return True  # Return True to allow magic link creation for testing
                
            # Construct magic link URL using frontend base URL
            base_url = settings.MAGIC_LINK_BASE_URL
            magic_link = f"{base_url}/auth/verify?token={token}"
            # #region agent log
            try:
                with open('/Users/evmacbook/the_edouard_company/mousealerts/.cursor/debug.log', 'a') as f:
                    f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"D","location":"sms.py:send_magic_link_sms","message":"Magic link constructed","data":{"magic_link":magic_link},"timestamp":int(datetime.now().timestamp()*1000)})+'\n')
            except: pass
            # #endregion
            
            # SMS message template
            message = f"""Your MouseAlerts login link: {magic_link}
Expires in 15 minutes. Reply STOP to opt out."""
            
            # Send SMS via Twilio
            # #region agent log
            try:
                with open('/Users/evmacbook/the_edouard_company/mousealerts/.cursor/debug.log', 'a') as f:
                    f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"sms.py:send_magic_link_sms","message":"Before Twilio API call","data":{"from_number":self.from_number,"to_phone":phone},"timestamp":int(datetime.now().timestamp()*1000)})+'\n')
            except: pass
            # #endregion
            message_obj = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=phone
            )
            # #region agent log
            try:
                with open('/Users/evmacbook/the_edouard_company/mousealerts/.cursor/debug.log', 'a') as f:
                    f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"sms.py:send_magic_link_sms","message":"Twilio API call succeeded","data":{"message_sid":message_obj.sid if message_obj else None},"timestamp":int(datetime.now().timestamp()*1000)})+'\n')
            except: pass
            # #endregion
            
            return message_obj.sid is not None
            
        except TwilioException as e:
            logger.error(f"Twilio SMS error: {e}")
            # #region agent log
            try:
                with open('/Users/evmacbook/the_edouard_company/mousealerts/.cursor/debug.log', 'a') as f:
                    f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B,C","location":"sms.py:send_magic_link_sms","message":"TwilioException caught","data":{"error_type":type(e).__name__,"error_code":getattr(e,'code',None),"error_msg":str(e),"error_status":getattr(e,'status',None)},"timestamp":int(datetime.now().timestamp()*1000)})+'\n')
            except: pass
            # #endregion
            return False
        except Exception as e:
            logger.error(f"SMS sending error: {e}")
            # #region agent log
            try:
                with open('/Users/evmacbook/the_edouard_company/mousealerts/.cursor/debug.log', 'a') as f:
                    f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C","location":"sms.py:send_magic_link_sms","message":"Generic Exception caught","data":{"error_type":type(e).__name__,"error_msg":str(e)},"timestamp":int(datetime.now().timestamp()*1000)})+'\n')
            except: pass
            # #endregion
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
