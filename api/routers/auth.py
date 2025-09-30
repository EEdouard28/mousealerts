"""
MouseAlerts API - Authentication Router

This router handles user authentication via magic link email flow.
No passwords are stored - users authenticate by clicking links sent to their email.

Endpoints:
- POST /magic-link: Send magic link email to user
- POST /verify: Verify magic link token and return JWT session

The magic link flow:
1. User enters email address
2. System sends email with time-limited token
3. User clicks link, token is verified
4. System returns JWT session token for API access

This provides passwordless authentication that's secure and user-friendly.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt
from datetime import datetime, timedelta
import uuid

from db import get_db
from config import settings
from models.user import User
from schemas.user import UserCreate, UserResponse
from services.email import send_magic_link_email

router = APIRouter()

@router.post("/magic-link")
async def send_magic_link(
    email: str,
    db: Session = Depends(get_db)
):
    """Send magic link email"""
    # Create or get user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            id=str(uuid.uuid4()),
            email=email
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Generate magic link token
    token_data = {
        "sub": user.id,
        "exp": datetime.utcnow() + timedelta(minutes=settings.MAGIC_LINK_EXPIRE_MINUTES)
    }
    token = jwt.encode(token_data, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    
    # Send magic link email
    magic_link = f"{settings.MAGIC_LINK_BASE_URL}/auth/verify?token={token}"
    await send_magic_link_email(email, magic_link)
    
    return {"message": "Magic link sent to your email"}

@router.post("/verify")
async def verify_magic_link(
    token: str,
    db: Session = Depends(get_db)
):
    """Verify magic link token and return JWT"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # Generate session JWT
    session_token_data = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    }
    session_token = jwt.encode(session_token_data, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    
    return {
        "access_token": session_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(db.query(User).filter(User.id == user_id).first())
    }
