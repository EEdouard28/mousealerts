"""
MouseAlerts API - Billing Router

This router handles Stripe subscription management and billing operations.
Users can view their current plan, upgrade/downgrade, and manage payments.

Endpoints:
- GET /plans: Get available subscription plans
- GET /current: Get user's current subscription
- POST /create-checkout: Create Stripe checkout session
- POST /stripe/webhook: Handle Stripe webhooks
- GET /portal: Get Stripe customer portal URL

Billing Flow:
1. User selects plan on frontend
2. Create Stripe checkout session
3. User completes payment on Stripe
4. Stripe webhook updates user subscription
5. User gains access to plan features

This router integrates with Stripe for secure payment processing
and subscription management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
import stripe

from db import get_db
from deps import get_current_active_user
from models.user import User
from models.plan import Plan
from models.subscription import Subscription
from config import settings

router = APIRouter()

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

@router.get("/plans")
async def get_available_plans(db: Session = Depends(get_db)):
    """Get all available subscription plans"""
    plans = db.query(Plan).all()
    return plans

@router.get("/current")
async def get_current_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's current subscription"""
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status == "active"
    ).first()
    
    if not subscription:
        return {"plan": "free", "status": "inactive"}
    
    plan = db.query(Plan).filter(Plan.id == subscription.plan_id).first()
    return {
        "plan": plan.name if plan else "free",
        "status": subscription.status,
        "current_period_end": subscription.current_period_end
    }

@router.post("/create-checkout")
async def create_checkout_session(
    price_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create Stripe checkout session for subscription"""
    try:
        checkout_session = stripe.checkout.Session.create(
            customer_email=current_user.email,
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=f"{settings.MAGIC_LINK_BASE_URL}/billing/success",
            cancel_url=f"{settings.MAGIC_LINK_BASE_URL}/billing/cancel",
            metadata={
                'user_id': current_user.id
            }
        )
        
        return {"checkout_url": checkout_session.url}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create checkout session: {str(e)}"
        )

@router.post("/stripe/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhook events"""
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle different event types
    if event['type'] == 'customer.subscription.created':
        # Handle new subscription
        subscription = event['data']['object']
        user_id = subscription['metadata'].get('user_id')
        if user_id:
            # Update user subscription in database
            pass
    
    elif event['type'] == 'customer.subscription.updated':
        # Handle subscription updates
        pass
    
    elif event['type'] == 'customer.subscription.deleted':
        # Handle subscription cancellations
        pass
    
    return {"status": "success"}

@router.get("/portal")
async def get_customer_portal(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get Stripe customer portal URL for subscription management"""
    try:
        portal_session = stripe.billing_portal.Session.create(
            customer_email=current_user.email,
            return_url=f"{settings.MAGIC_LINK_BASE_URL}/billing"
        )
        
        return {"portal_url": portal_session.url}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create portal session: {str(e)}"
        )
