"""
MouseAlerts API - Authentication Router

This router handles user authentication via SMS magic link flow.
No passwords are stored - users authenticate by clicking links sent to their phone via SMS.

Endpoints:
- POST /magic-link: Send magic link SMS to user
- GET /verify: Verify magic link token and return JWT session

The SMS magic link flow:
1. User enters phone number
2. System sends SMS with time-limited token link
3. User clicks link, token is verified
4. System returns JWT session token for API access

This provides mobile-first passwordless authentication that's perfect for Disney families.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from jose import jwt
from datetime import datetime, timedelta
import uuid

from db import get_db
from config import settings
from models.user import User
from schemas.user import UserCreate, UserResponse
from schemas.magic_link import (
    MagicLinkRequest,
    MagicLinkResponse,
    MagicLinkVerifyResponse,
    RateLimitResponse,
    ErrorResponse
)
from services.sms import SMSService

router = APIRouter()

@router.post("/magic-link", response_model=MagicLinkResponse)
async def send_magic_link(
    request: MagicLinkRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Send magic link SMS to user's phone"""
    
    sms_service = SMSService()
    
    # Check rate limiting
    rate_limit_status = sms_service.get_rate_limit_status(db, request.phone)
    if rate_limit_status["is_rate_limited"]:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later.",
            headers={"Retry-After": "3600"}  # 1 hour
        )
    
    # Create magic link token
    magic_token = sms_service.create_magic_link_token(
        db=db,
        phone=request.phone,
        ip_address=http_request.client.host if http_request.client else None,
        user_agent=http_request.headers.get("user-agent")
    )
    
    # Send SMS (gracefully handle failures for testing/demo)
    # #region agent log
    import json
    from datetime import datetime
    try:
        with open('/Users/evmacbook/the_edouard_company/mousealerts/.cursor/debug.log', 'a') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B,C","location":"auth.py:send_magic_link","message":"Before calling send_magic_link_sms","data":{"phone":request.phone,"has_twilio_sid":bool(settings.TWILIO_ACCOUNT_SID),"has_twilio_token":bool(settings.TWILIO_AUTH_TOKEN)},"timestamp":int(datetime.now().timestamp()*1000)})+'\n')
    except: pass
    # #endregion
    sms_sent = sms_service.send_magic_link_sms(request.phone, magic_token.token)
    # #region agent log
    try:
        with open('/Users/evmacbook/the_edouard_company/mousealerts/.cursor/debug.log', 'a') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B,C","location":"auth.py:send_magic_link","message":"After calling send_magic_link_sms","data":{"sms_sent":sms_sent},"timestamp":int(datetime.now().timestamp()*1000)})+'\n')
    except: pass
    # #endregion
    
    # If SMS fails but we're in testing mode (no Twilio configured), still return success
    # The magic link token is created and can be used for testing
    if not sms_sent:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"SMS sending failed for {request.phone}, but token was created")
        # #region agent log
        try:
            with open('/Users/evmacbook/the_edouard_company/mousealerts/.cursor/debug.log', 'a') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"auth.py:send_magic_link","message":"SMS sending failed, checking Twilio config","data":{"has_twilio_sid":bool(settings.TWILIO_ACCOUNT_SID),"has_twilio_token":bool(settings.TWILIO_AUTH_TOKEN)},"timestamp":int(datetime.now().timestamp()*1000)})+'\n')
        except: pass
        # #endregion
        
        # Check if Twilio is configured
        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
            # In testing mode without Twilio, return success with a note
            return MagicLinkResponse(
                success=True,
                message=f"Magic link created (SMS not configured - use token: {magic_token.token})",
                expires_in_minutes=15
            )
        else:
            # Twilio is configured but failed - return error
            # #region agent log
            try:
                with open('/Users/evmacbook/the_edouard_company/mousealerts/.cursor/debug.log', 'a') as f:
                    f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B,C","location":"auth.py:send_magic_link","message":"Raising HTTPException - Twilio configured but SMS failed","data":{},"timestamp":int(datetime.now().timestamp()*1000)})+'\n')
            except: pass
            # #endregion
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send SMS. Please try again."
            )
    
    return MagicLinkResponse(
        success=True,
        message=f"Magic link sent to {request.phone}",
        expires_in_minutes=15
    )

@router.get("/verify", response_model=MagicLinkVerifyResponse)
async def verify_magic_link(
    token: str,
    db: Session = Depends(get_db)
):
    """Verify magic link token and return JWT session"""
    
    sms_service = SMSService()
    
    # Verify token
    magic_token = sms_service.verify_magic_link_token(db, token)
    
    if not magic_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    # Create or get user
    user = db.query(User).filter(User.email == magic_token.phone).first()
    if not user:
        user = User(
            id=str(uuid.uuid4()),
            email=magic_token.phone,  # Store phone as email for now
            phone=magic_token.phone
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Generate session JWT
    session_token_data = {
        "sub": str(user.id),
        "exp": datetime.utcnow() + timedelta(hours=24)  # 24 hour session
    }
    session_token = jwt.encode(
        session_token_data, 
        settings.JWT_SECRET, 
        algorithm="HS256"
    )
    
    return MagicLinkVerifyResponse(
        success=True,
        access_token=session_token,
        token_type="bearer",
        expires_in=86400,  # 24 hours
        user_id=str(user.id),
        message="Login successful"
    )

@router.get("/rate-limit/{phone}", response_model=RateLimitResponse)
async def check_rate_limit(
    phone: str,
    db: Session = Depends(get_db)
):
    """Check rate limiting status for a phone number"""
    
    sms_service = SMSService()
    rate_limit_status = sms_service.get_rate_limit_status(db, phone)
    
    return RateLimitResponse(**rate_limit_status)
