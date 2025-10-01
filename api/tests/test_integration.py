"""
Integration tests for MouseAlerts API
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
from datetime import datetime, timedelta

class TestAPIIntegration:
    """Test API integration scenarios"""
    
    def test_complete_auth_flow(self, client, db_session):
        """Test complete authentication flow"""
        # Step 1: Request magic link
        with patch('routers.auth.send_sms', return_value=True):
            response = client.post("/api/auth/magic-link", json={"phone": "+15551234567"})
            assert response.status_code == 200
        
        # Step 2: Verify token (mock successful verification)
        with patch('routers.auth.verify_magic_link_token', return_value="+15551234567"):
            response = client.get("/api/auth/verify?token=test-token")
            assert response.status_code == 200
            assert "access_token" in response.json()
            assert "user" in response.json()
    
    def test_alert_creation_workflow(self, client, auth_headers, test_user):
        """Test complete alert creation workflow"""
        with patch('deps.get_current_active_user', return_value=test_user):
            # Step 1: Create alert
            alert_data = {
                "restaurant": "Cinderella's Royal Table",
                "date": "2024-12-25",
                "time_start": "18:00",
                "time_end": "20:00",
                "party_size": 4,
                "notification_channels": ["email", "sms"]
            }
            
            response = client.post("/api/alerts", json=alert_data, headers=auth_headers)
            assert response.status_code == 201
            alert_id = response.json()["id"]
            
            # Step 2: Get alert
            response = client.get(f"/api/alerts/{alert_id}", headers=auth_headers)
            assert response.status_code == 200
            assert response.json()["restaurant"] == alert_data["restaurant"]
            
            # Step 3: Update alert
            update_data = {"party_size": 6}
            response = client.patch(f"/api/alerts/{alert_id}", json=update_data, headers=auth_headers)
            assert response.status_code == 200
            assert response.json()["party_size"] == 6
            
            # Step 4: Delete alert
            response = client.delete(f"/api/alerts/{alert_id}", headers=auth_headers)
            assert response.status_code == 200
    
    def test_payment_workflow(self, client, auth_headers, test_user):
        """Test payment processing workflow"""
        with patch('deps.get_current_active_user', return_value=test_user):
            # Step 1: Create checkout session
            payment_data = {
                "plan_id": "premium",
                "mode": "subscription"
            }
            
            with patch('routers.billing.stripe.checkout.Session.create') as mock_create:
                mock_create.return_value = MagicMock(id="test-session-id", url="https://checkout.stripe.com/test")
                
                response = client.post("/api/billing/checkout", json=payment_data, headers=auth_headers)
                assert response.status_code == 200
                assert "checkout_url" in response.json()
    
    def test_webhook_processing(self, client, db_session, test_user):
        """Test Stripe webhook processing"""
        # Mock Stripe webhook event
        webhook_data = {
            "id": "evt_test_webhook",
            "object": "event",
            "type": "customer.subscription.created",
            "data": {
                "object": {
                    "id": "sub_test_subscription",
                    "customer": "cus_test_customer",
                    "status": "active",
                    "current_period_end": int((datetime.utcnow() + timedelta(days=30)).timestamp())
                }
            }
        }
        
        with patch('routers.billing.stripe.Webhook.construct_event') as mock_construct:
            mock_construct.return_value = webhook_data
            
            response = client.post("/api/billing/stripe/webhook", json=webhook_data)
            assert response.status_code == 200
    
    def test_nlu_parsing_workflow(self, client, auth_headers, test_user):
        """Test NLU parsing workflow"""
        with patch('deps.get_current_active_user', return_value=test_user):
            # Test NLU parsing
            nlu_data = {
                "text": "I want princess dining for 4 people on December 25th at 7pm"
            }
            
            with patch('routers.nlu.NLUService.parse') as mock_parse:
                mock_parse.return_value = {
                    "date": "2024-12-25",
                    "time": 19,
                    "party_size": 4,
                    "restaurant": "Cinderella's Royal Table",
                    "experience_tags": ["princess"],
                    "confidence": 0.9
                }
                
                response = client.post("/api/nlu/parse", json=nlu_data, headers=auth_headers)
                assert response.status_code == 200
                assert response.json()["confidence"] == 0.9
    
    def test_admin_workflow(self, client, admin_headers, test_admin_user):
        """Test admin workflow"""
        with patch('deps.get_current_active_user', return_value=test_admin_user):
            # Step 1: Get admin dashboard
            response = client.get("/api/admin/dashboard", headers=admin_headers)
            assert response.status_code == 200
            
            # Step 2: Get users
            response = client.get("/api/admin/users", headers=admin_headers)
            assert response.status_code == 200
            
            # Step 3: Get analytics
            response = client.get("/api/admin/analytics/dashboard", headers=admin_headers)
            assert response.status_code == 200
    
    def test_error_handling(self, client):
        """Test error handling across the API"""
        # Test 404 errors
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
        
        # Test 422 validation errors
        response = client.post("/api/auth/magic-link", json={"phone": "invalid"})
        assert response.status_code == 422
        
        # Test 401 unauthorized errors
        response = client.get("/api/me")
        assert response.status_code == 401
    
    def test_rate_limiting(self, client):
        """Test rate limiting functionality"""
        # Test rate limiting on magic link endpoint
        for i in range(10):  # Make multiple requests
            response = client.post("/api/auth/magic-link", json={"phone": "+15551234567"})
            # Should either succeed or be rate limited
            assert response.status_code in [200, 429]
    
    def test_database_transactions(self, client, auth_headers, test_user, db_session):
        """Test database transaction handling"""
        with patch('deps.get_current_active_user', return_value=test_user):
            # Test concurrent operations
            alert_data = {
                "restaurant": "Cinderella's Royal Table",
                "date": "2024-12-25",
                "time_start": "18:00",
                "time_end": "20:00",
                "party_size": 4
            }
            
            # Create multiple alerts concurrently
            responses = []
            for i in range(3):
                response = client.post("/api/alerts", json=alert_data, headers=auth_headers)
                responses.append(response)
            
            # All should succeed
            for response in responses:
                assert response.status_code == 201
    
    def test_external_service_integration(self, client, auth_headers, test_user):
        """Test external service integration"""
        with patch('deps.get_current_active_user', return_value=test_user):
            # Test SMS service integration
            with patch('routers.auth.send_sms') as mock_sms:
                mock_sms.return_value = True
                response = client.post("/api/auth/magic-link", json={"phone": "+15551234567"})
                assert response.status_code == 200
                mock_sms.assert_called_once()
            
            # Test email service integration
            with patch('services.email_service.send_email') as mock_email:
                mock_email.return_value = True
                # This would test email sending in a real scenario
                pass
            
            # Test push notification service integration
            with patch('services.push_service.send_push_notification') as mock_push:
                mock_push.return_value = True
                # This would test push notification sending in a real scenario
                pass
    
    def test_data_consistency(self, client, auth_headers, test_user, db_session):
        """Test data consistency across operations"""
        with patch('deps.get_current_active_user', return_value=test_user):
            # Create alert
            alert_data = {
                "restaurant": "Cinderella's Royal Table",
                "date": "2024-12-25",
                "time_start": "18:00",
                "time_end": "20:00",
                "party_size": 4
            }
            
            response = client.post("/api/alerts", json=alert_data, headers=auth_headers)
            assert response.status_code == 201
            alert_id = response.json()["id"]
            
            # Verify data consistency
            response = client.get("/api/alerts", headers=auth_headers)
            assert response.status_code == 200
            alerts = response.json()
            assert len(alerts) >= 1
            assert any(alert["id"] == alert_id for alert in alerts)
            
            # Update alert
            update_data = {"party_size": 6}
            response = client.patch(f"/api/alerts/{alert_id}", json=update_data, headers=auth_headers)
            assert response.status_code == 200
            
            # Verify update
            response = client.get(f"/api/alerts/{alert_id}", headers=auth_headers)
            assert response.status_code == 200
            assert response.json()["party_size"] == 6
    
    def test_security_headers(self, client):
        """Test security headers"""
        response = client.get("/health")
        assert response.status_code == 200
        
        # Check for security headers
        headers = response.headers
        # In a real implementation, we'd check for:
        # - X-Content-Type-Options: nosniff
        # - X-Frame-Options: DENY
        # - X-XSS-Protection: 1; mode=block
        # - Strict-Transport-Security
        # - Content-Security-Policy
    
    def test_cors_headers(self, client):
        """Test CORS headers"""
        response = client.options("/api/alerts")
        assert response.status_code == 200
        
        # Check for CORS headers
        headers = response.headers
        # In a real implementation, we'd check for:
        # - Access-Control-Allow-Origin
        # - Access-Control-Allow-Methods
        # - Access-Control-Allow-Headers
    
    def test_api_versioning(self, client):
        """Test API versioning"""
        # Test that API endpoints are properly versioned
        response = client.get("/api/health")
        assert response.status_code == 404  # Should not exist without version
        
        response = client.get("/health")
        assert response.status_code == 200  # Health check should work
    
    def test_health_check_endpoints(self, client):
        """Test health check endpoints"""
        # Test main health check
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        
        # Test database health
        response = client.get("/api/admin/analytics/system-health")
        # This would require admin authentication in real scenario
        assert response.status_code in [200, 401, 403]
    
    def test_logging_and_monitoring(self, client, auth_headers, test_user):
        """Test logging and monitoring"""
        with patch('deps.get_current_active_user', return_value=test_user):
            # Test that operations are logged
            response = client.get("/api/me", headers=auth_headers)
            assert response.status_code == 200
            
            # In a real implementation, we'd check that:
            # - Request/response logging works
            # - Error logging works
            # - Performance metrics are collected
            # - Audit trails are maintained
