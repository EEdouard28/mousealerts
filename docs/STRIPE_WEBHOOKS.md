# Stripe Webhook Integration

This document describes the Stripe webhook integration for MouseAlerts, including event handling, plan updates, and testing procedures.

## Overview

The webhook system handles Stripe payment events to automatically update user subscriptions and plan access. This ensures users get immediate access to features after payment and lose access when payments fail.

## Webhook Endpoint

**URL:** `POST /billing/stripe/webhook`  
**Authentication:** Stripe signature verification  
**Content-Type:** `application/json`

## Supported Events

### 1. Subscription Events

#### `customer.subscription.created`
- **Trigger:** New subscription created
- **Action:** Create subscription record in database
- **Updates:** User plan, feature access

#### `customer.subscription.updated`
- **Trigger:** Subscription modified (plan change, billing cycle)
- **Action:** Update subscription record
- **Updates:** Plan limits, billing period

#### `customer.subscription.deleted`
- **Trigger:** Subscription cancelled
- **Action:** Mark subscription as cancelled
- **Updates:** Revert to free plan

### 2. Payment Events

#### `invoice.payment_succeeded`
- **Trigger:** Successful payment
- **Action:** Activate subscription
- **Updates:** Plan status to "active"

#### `invoice.payment_failed`
- **Trigger:** Failed payment
- **Action:** Mark subscription as past due
- **Updates:** Plan status to "past_due"

### 3. One-Time Payment Events

#### `checkout.session.completed`
- **Trigger:** One-time payment completed
- **Action:** Create temporary subscription
- **Updates:** Grant single alert access

## Plan Types

### Free Plan (Default)
```json
{
  "plan_id": "free",
  "plan_name": "Free",
  "limits": {
    "alerts_per_user": 2,
    "notification_channels": ["email"],
    "instant_notifications": false,
    "ai_prompt_bar": false,
    "priority_support": false,
    "monitoring_interval": 15
  }
}
```

### Single Alert Plan
```json
{
  "plan_id": "single_alert",
  "plan_name": "Single Alert",
  "limits": {
    "alerts_per_user": 1,
    "notification_channels": ["email", "sms"],
    "instant_notifications": true,
    "ai_prompt_bar": false,
    "priority_support": true,
    "monitoring_interval": 5
  }
}
```

### Premium Plan
```json
{
  "plan_id": "price_premium",
  "plan_name": "Premium",
  "limits": {
    "alerts_per_user": 25,
    "notification_channels": ["email", "sms"],
    "instant_notifications": true,
    "ai_prompt_bar": true,
    "priority_support": true,
    "monitoring_interval": 5
  }
}
```

### Family Plan
```json
{
  "plan_id": "price_family",
  "plan_name": "Family",
  "limits": {
    "alerts_per_user": -1,  // unlimited
    "notification_channels": ["email", "sms", "push"],
    "instant_notifications": true,
    "ai_prompt_bar": true,
    "priority_support": true,
    "monitoring_interval": 1
  }
}
```

## Database Schema

### Subscriptions Table
```sql
CREATE TABLE subscriptions (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    plan_id VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    current_period_start INTEGER,
    current_period_end INTEGER,
    stripe_subscription_id VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Testing

### Manual Testing
```bash
# Start the API server
cd api
python -m uvicorn main:app --reload

# Run webhook tests
python test_webhook_manual.py
```

### Automated Testing
```bash
# Run webhook tests
pytest api/tests/test_webhooks.py -v
```

### Test Scenarios
1. **Subscription Creation** - User upgrades to Premium
2. **Single Alert Purchase** - User buys one-time alert
3. **Payment Success** - Subscription activated
4. **Payment Failure** - Subscription marked as past due
5. **Subscription Cancellation** - User downgrades to Free

## Error Handling

### Invalid Signature
- **Status:** 400 Bad Request
- **Response:** `{"detail": "Invalid signature"}`
- **Action:** Log security event, reject request

### Invalid Payload
- **Status:** 400 Bad Request
- **Response:** `{"detail": "Invalid payload"}`
- **Action:** Log error, reject request

### Database Errors
- **Status:** 500 Internal Server Error
- **Response:** `{"detail": "Database error"}`
- **Action:** Log error, rollback transaction

## Security

### Signature Verification
All webhooks must include valid Stripe signature:
```
stripe-signature: t=timestamp,v1=signature
```

### Rate Limiting
- **Limit:** 100 requests per minute per IP
- **Action:** Return 429 Too Many Requests

### Logging
All webhook events are logged with:
- Event type
- User ID
- Timestamp
- Success/failure status

## Monitoring

### Health Checks
- **Endpoint:** `GET /billing/webhook/health`
- **Response:** `{"status": "healthy", "last_webhook": timestamp}`

### Metrics
- Webhook success rate
- Processing time
- Error frequency
- Plan upgrade/downgrade counts

## Troubleshooting

### Common Issues

1. **Webhook not received**
   - Check Stripe dashboard for webhook status
   - Verify endpoint URL is correct
   - Check server logs for errors

2. **Plan not updated**
   - Verify webhook signature is valid
   - Check database connection
   - Review subscription record

3. **Payment not processed**
   - Check Stripe dashboard for payment status
   - Verify webhook event was sent
   - Review error logs

### Debug Mode
Enable debug logging:
```python
import logging
logging.getLogger("stripe").setLevel(logging.DEBUG)
```

## Production Deployment

### Environment Variables
```bash
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
DATABASE_URL=postgresql://...
```

### Webhook Configuration
1. Add webhook endpoint in Stripe dashboard
2. Select events to listen for
3. Test webhook delivery
4. Monitor webhook logs

### Monitoring Setup
1. Set up alerts for webhook failures
2. Monitor subscription status changes
3. Track payment success rates
4. Monitor plan enforcement

## API Reference

### Webhook Endpoint
```http
POST /billing/stripe/webhook
Content-Type: application/json
stripe-signature: t=timestamp,v1=signature

{
  "id": "evt_...",
  "object": "event",
  "type": "customer.subscription.created",
  "data": {
    "object": {
      "id": "sub_...",
      "status": "active",
      "metadata": {
        "user_id": "user_123"
      }
    }
  }
}
```

### Response
```json
{
  "status": "success"
}
```

## Support

For webhook-related issues:
1. Check Stripe dashboard for webhook delivery status
2. Review server logs for error messages
3. Test webhook endpoint manually
4. Contact support with webhook ID and timestamp
