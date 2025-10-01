"""
Manual Stripe Webhook Testing

This script helps test Stripe webhook integration manually.
It simulates webhook events and validates the responses.

Usage:
    python test_webhook_manual.py

This will test various webhook scenarios to ensure
the payment system works correctly.
"""

import requests
import json
import time
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
WEBHOOK_URL = f"{BASE_URL}/billing/stripe/webhook"

# Test webhook payloads
test_payloads = {
    "subscription_created": {
        "id": "evt_test_subscription_created",
        "object": "event",
        "type": "customer.subscription.created",
        "data": {
            "object": {
                "id": "sub_test123",
                "object": "subscription",
                "status": "active",
                "current_period_start": int(time.time()),
                "current_period_end": int(time.time()) + 86400 * 30,  # 30 days
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
    },
    
    "single_alert_purchase": {
        "id": "evt_test_single_alert",
        "object": "event",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_single_alert_test",
                "object": "checkout.session",
                "created": int(time.time()),
                "metadata": {
                    "user_id": "user_test123",
                    "type": "single_alert"
                }
            }
        }
    },
    
    "payment_succeeded": {
        "id": "evt_test_payment_succeeded",
        "object": "event",
        "type": "invoice.payment_succeeded",
        "data": {
            "object": {
                "id": "in_test123",
                "object": "invoice",
                "subscription": "sub_test123"
            }
        }
    },
    
    "payment_failed": {
        "id": "evt_test_payment_failed",
        "object": "event",
        "type": "invoice.payment_failed",
        "data": {
            "object": {
                "id": "in_test123",
                "object": "invoice",
                "subscription": "sub_test123"
            }
        }
    },
    
    "subscription_cancelled": {
        "id": "evt_test_subscription_cancelled",
        "object": "event",
        "type": "customer.subscription.deleted",
        "data": {
            "object": {
                "id": "sub_test123",
                "object": "subscription",
                "status": "canceled",
                "metadata": {
                    "user_id": "user_test123"
                }
            }
        }
    }
}

def test_webhook_endpoint(payload_name, payload):
    """Test a specific webhook endpoint"""
    print(f"\n🧪 Testing {payload_name}...")
    
    headers = {
        "Content-Type": "application/json",
        "stripe-signature": "test_signature"
    }
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            headers=headers,
            timeout=10
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            print(f"   ✅ {payload_name} - SUCCESS")
        else:
            print(f"   ❌ {payload_name} - FAILED")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ {payload_name} - ERROR: {e}")

def test_all_webhooks():
    """Test all webhook scenarios"""
    print("🚀 Starting Stripe Webhook Testing")
    print("=" * 50)
    
    # Check if server is running
    try:
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        if health_response.status_code != 200:
            print("❌ Server is not running. Please start the API server first.")
            return
    except requests.exceptions.RequestException:
        print("❌ Server is not running. Please start the API server first.")
        return
    
    print("✅ Server is running")
    
    # Test each webhook scenario
    for payload_name, payload in test_payloads.items():
        test_webhook_endpoint(payload_name, payload)
        time.sleep(1)  # Small delay between tests
    
    print("\n" + "=" * 50)
    print("🎉 Webhook testing completed!")
    print("\nNext steps:")
    print("1. Check the database for subscription records")
    print("2. Verify plan enforcement is working")
    print("3. Test the frontend billing flow")

def test_plan_enforcement():
    """Test plan enforcement after webhook events"""
    print("\n🔒 Testing Plan Enforcement...")
    
    # Test plan info endpoint
    try:
        response = requests.get(f"{BASE_URL}/alerts/plan-info")
        print(f"   Plan Info Status: {response.status_code}")
        if response.status_code == 200:
            plan_info = response.json()
            print(f"   Plan: {plan_info.get('plan', {}).get('plan_name', 'Unknown')}")
            print(f"   Usage: {plan_info.get('usage', {})}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Plan enforcement test failed: {e}")

if __name__ == "__main__":
    print("MouseAlerts - Stripe Webhook Testing")
    print("====================================")
    
    # Test webhooks
    test_all_webhooks()
    
    # Test plan enforcement
    test_plan_enforcement()
    
    print("\n📋 Test Summary:")
    print("- Subscription creation webhook")
    print("- Single alert purchase webhook") 
    print("- Payment success/failure webhooks")
    print("- Subscription cancellation webhook")
    print("- Plan enforcement validation")
    
    print("\n✨ All tests completed!")
