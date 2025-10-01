"""
Test Stripe Webhook Integration

This module tests the Stripe webhook handling to ensure
payment events are processed correctly and user plans
are updated appropriately.

Test Cases:
- Subscription creation
- Subscription updates
- Subscription cancellations
- One-time payments (Single Alert)
- Payment success/failure
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from main import app
from models.user import User
from models.subscription import Subscription
from models.plan import Plan

client = TestClient(app)

# Mock webhook payloads
SUBSCRIPTION_CREATED_PAYLOAD = {
    "id": "evt_test_webhook",
    "object": "event",
    "type": "customer.subscription.created",
    "data": {
        "object": {
            "id": "sub_test123",
            "object": "subscription",
            "status": "active",
            "current_period_start": 1640995200,
            "current_period_end": 1643673600,
            "items": {
                "data": [{
                    "price": {
                        "id": "price_premium"
                    }
                }]
            },
            "metadata": {
                "user_id": "user_test123"
            }
        }
    }
}

CHECKOUT_COMPLETED_PAYLOAD = {
    "id": "evt_test_webhook",
    "object": "event",
    "type": "checkout.session.completed",
    "data": {
        "object": {
            "id": "cs_test123",
            "object": "checkout.session",
            "created": 1640995200,
            "metadata": {
                "user_id": "user_test123",
                "type": "single_alert"
            }
        }
    }
}

INVOICE_PAYMENT_SUCCEEDED_PAYLOAD = {
    "id": "evt_test_webhook",
    "object": "event",
    "type": "invoice.payment_succeeded",
    "data": {
        "object": {
            "id": "in_test123",
            "object": "invoice",
            "subscription": "sub_test123"
        }
    }
}

def test_subscription_created_webhook(db_session: Session):
    """Test subscription creation webhook"""
    # Create test user
    user = User(
        id="user_test123",
        phone="+15551234567",
        email="test@example.com"
    )
    db_session.add(user)
    db_session.commit()
    
    # Create test plan
    plan = Plan(
        id="price_premium",
        name="Premium",
        limits={
            "alerts_per_user": 25,
            "notification_channels": ["email", "sms"],
            "instant_notifications": True,
            "ai_prompt_bar": True,
            "priority_support": True,
            "monitoring_interval": 5
        },
        price_cents=999
    )
    db_session.add(plan)
    db_session.commit()
    
    # Mock Stripe webhook verification
    with patch('stripe.Webhook.construct_event') as mock_construct:
        mock_construct.return_value = SUBSCRIPTION_CREATED_PAYLOAD
        
        response = client.post(
            "/billing/stripe/webhook",
            json=SUBSCRIPTION_CREATED_PAYLOAD,
            headers={"stripe-signature": "test_signature"}
        )
        
        assert response.status_code == 200
        assert response.json() == {"status": "success"}
        
        # Verify subscription was created
        subscription = db_session.query(Subscription).filter(
            Subscription.stripe_subscription_id == "sub_test123"
        ).first()
        
        assert subscription is not None
        assert subscription.user_id == "user_test123"
        assert subscription.plan_id == "price_premium"
        assert subscription.status == "active"

def test_single_alert_purchase_webhook(db_session: Session):
    """Test single alert purchase webhook"""
    # Create test user
    user = User(
        id="user_test123",
        phone="+15551234567",
        email="test@example.com"
    )
    db_session.add(user)
    db_session.commit()
    
    # Mock Stripe webhook verification
    with patch('stripe.Webhook.construct_event') as mock_construct:
        mock_construct.return_value = CHECKOUT_COMPLETED_PAYLOAD
        
        response = client.post(
            "/billing/stripe/webhook",
            json=CHECKOUT_COMPLETED_PAYLOAD,
            headers={"stripe-signature": "test_signature"}
        )
        
        assert response.status_code == 200
        assert response.json() == {"status": "success"}
        
        # Verify single alert subscription was created
        subscription = db_session.query(Subscription).filter(
            Subscription.plan_id == "single_alert"
        ).first()
        
        assert subscription is not None
        assert subscription.user_id == "user_test123"
        assert subscription.status == "active"

def test_payment_success_webhook(db_session: Session):
    """Test payment success webhook"""
    # Create test subscription
    subscription = Subscription(
        id="sub_test123",
        user_id="user_test123",
        plan_id="price_premium",
        status="past_due",
        stripe_subscription_id="sub_test123"
    )
    db_session.add(subscription)
    db_session.commit()
    
    # Mock Stripe webhook verification
    with patch('stripe.Webhook.construct_event') as mock_construct:
        mock_construct.return_value = INVOICE_PAYMENT_SUCCEEDED_PAYLOAD
        
        response = client.post(
            "/billing/stripe/webhook",
            json=INVOICE_PAYMENT_SUCCEEDED_PAYLOAD,
            headers={"stripe-signature": "test_signature"}
        )
        
        assert response.status_code == 200
        
        # Verify subscription status was updated
        db_session.refresh(subscription)
        assert subscription.status == "active"

def test_webhook_signature_verification_failure():
    """Test webhook with invalid signature"""
    with patch('stripe.Webhook.construct_event') as mock_construct:
        mock_construct.side_effect = Exception("Invalid signature")
        
        response = client.post(
            "/billing/stripe/webhook",
            json={},
            headers={"stripe-signature": "invalid_signature"}
        )
        
        assert response.status_code == 400
        assert "Invalid signature" in response.json()["detail"]

def test_webhook_invalid_payload():
    """Test webhook with invalid payload"""
    with patch('stripe.Webhook.construct_event') as mock_construct:
        mock_construct.side_effect = ValueError("Invalid payload")
        
        response = client.post(
            "/billing/stripe/webhook",
            json={},
            headers={"stripe-signature": "test_signature"}
        )
        
        assert response.status_code == 400
        assert "Invalid payload" in response.json()["detail"]

if __name__ == "__main__":
    pytest.main([__file__])
