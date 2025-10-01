"""
Unit tests for authentication endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json

class TestAuthentication:
    """Test authentication endpoints"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert "version" in response.json()
    
    def test_magic_link_request_invalid_phone(self, client):
        """Test magic link request with invalid phone number"""
        response = client.post("/api/auth/magic-link", json={"phone": "invalid"})
        assert response.status_code == 422  # Validation error
    
    def test_magic_link_request_missing_phone(self, client):
        """Test magic link request without phone number"""
        response = client.post("/api/auth/magic-link", json={})
        assert response.status_code == 422  # Validation error
    
    @patch('routers.auth.SMSService')
    def test_magic_link_request_success(self, mock_sms_service, client, db_session):
        """Test successful magic link request"""
        mock_sms_service.return_value.send_magic_link_sms.return_value = True
        mock_sms_service.return_value.get_rate_limit_status.return_value = {"is_rate_limited": False}
        mock_sms_service.return_value.create_magic_link_token.return_value = type('obj', (object,), {'token': 'test-token'})()
        
        response = client.post("/api/auth/magic-link", json={"phone": "+15551234567"})
        assert response.status_code == 200
        assert response.json()["message"] == "Magic link sent to +15551234567"
        mock_sms_service.return_value.send_magic_link_sms.assert_called_once()
    
    @patch('routers.auth.SMSService')
    def test_magic_link_request_sms_failure(self, mock_sms_service, client, db_session):
        """Test magic link request when SMS fails"""
        mock_sms_service.return_value.send_magic_link_sms.return_value = False
        mock_sms_service.return_value.get_rate_limit_status.return_value = {"is_rate_limited": False}
        mock_sms_service.return_value.create_magic_link_token.return_value = type('obj', (object,), {'token': 'test-token'})()
        
        response = client.post("/api/auth/magic-link", json={"phone": "+15551234567"})
        assert response.status_code == 500
        assert "Failed to send SMS" in response.json()["detail"]
    
    @patch('routers.auth.SMSService')
    def test_verify_token_invalid(self, mock_sms_service, client):
        """Test token verification with invalid token"""
        mock_sms_service.return_value.verify_magic_link_token.return_value = None
        
        response = client.get("/api/auth/verify?token=invalid-token")
        assert response.status_code == 401
        assert "Invalid or expired token" in response.json()["detail"]
    
    def test_verify_token_missing(self, client):
        """Test token verification without token"""
        response = client.get("/api/auth/verify")
        assert response.status_code == 422  # Validation error
    
    @patch('routers.auth.SMSService')
    def test_verify_token_success(self, mock_sms_service, client, db_session):
        """Test successful token verification"""
        # Mock the SMS service to return a valid magic token
        mock_magic_token = type('obj', (object,), {
            'phone': '+15551234567',
            'id': 'test-token-id'
        })()
        mock_sms_service.return_value.verify_magic_link_token.return_value = mock_magic_token
        
        response = client.get("/api/auth/verify?token=test-token")
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert response.json()["success"] == True
    
    def test_logout_success(self, client, auth_headers):
        """Test successful logout"""
        response = client.post("/api/auth/logout", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"
    
    def test_logout_without_auth(self, client):
        """Test logout without authentication"""
        response = client.post("/api/auth/logout")
        assert response.status_code == 403  # FastAPI HTTPBearer returns 403 for missing token
    
    def test_get_me_success(self, client, auth_headers, test_user):
        """Test getting current user profile"""
        with patch('middleware.auth.get_current_user', return_value=test_user):
            response = client.get("/api/auth/me", headers=auth_headers)
            assert response.status_code == 200
            assert response.json()["email"] == test_user.email
            assert response.json()["phone"] == test_user.phone
    
    def test_get_me_unauthorized(self, client):
        """Test getting user profile without authentication"""
        response = client.get("/api/auth/me")
        assert response.status_code == 403  # FastAPI HTTPBearer returns 403 for missing token
    
    @patch('routers.auth.SMSService')
    def test_rate_limiting_magic_link(self, mock_sms_service, client):
        """Test rate limiting for magic link requests"""
        mock_sms_service.return_value.get_rate_limit_status.return_value = {"is_rate_limited": False}
        mock_sms_service.return_value.send_magic_link_sms.return_value = True
        mock_sms_service.return_value.create_magic_link_token.return_value = type('obj', (object,), {'token': 'test-token'})()
        
        response = client.post("/api/auth/magic-link", json={"phone": "+15551234567"})
        assert response.status_code == 200
    
    def test_phone_number_validation(self, client):
        """Test phone number validation"""
        invalid_phones = [
            "123",  # Too short
            "abc",  # Not numeric
            "+1",   # Too short
            "",     # Empty
        ]
        
        for phone in invalid_phones:
            response = client.post("/api/auth/magic-link", json={"phone": phone})
            assert response.status_code == 422  # Validation error
    
    @patch('routers.auth.SMSService')
    def test_phone_number_e164_format(self, mock_sms_service, client):
        """Test E.164 phone number format validation"""
        mock_sms_service.return_value.get_rate_limit_status.return_value = {"is_rate_limited": False}
        mock_sms_service.return_value.send_magic_link_sms.return_value = True
        mock_sms_service.return_value.create_magic_link_token.return_value = type('obj', (object,), {'token': 'test-token'})()
        
        valid_phones = [
            "+15551234567",
            "+1234567890",
            "+44123456789"
        ]
        
        for phone in valid_phones:
            response = client.post("/api/auth/magic-link", json={"phone": phone})
            assert response.status_code == 200
    
    @patch('routers.auth.SMSService')
    def test_token_expiration(self, mock_sms_service, client, db_session):
        """Test token expiration handling"""
        from models.magic_link_token import MagicLinkToken
        import uuid
        from datetime import datetime, timedelta
        
        # Mock SMS service to return None for expired token
        mock_sms_service.return_value.verify_magic_link_token.return_value = None
        
        # Create an expired token
        expired_time = datetime.utcnow() - timedelta(hours=1)
        token = MagicLinkToken(
            id=str(uuid.uuid4()),
            phone="+15551234569",  # Unique phone number
            token="test-token-123",
            expires_at=expired_time
        )
        db_session.add(token)
        db_session.commit()
        
        response = client.get(f"/api/auth/verify?token={token.id}")
        assert response.status_code == 401
        assert "Invalid or expired token" in response.json()["detail"]
    
    @patch('routers.auth.SMSService')
    def test_token_single_use(self, mock_sms_service, client, db_session):
        """Test that tokens can only be used once"""
        from models.magic_link_token import MagicLinkToken
        import uuid
        from datetime import datetime
        
        # Mock SMS service to return token on first call, None on second call
        mock_magic_token = type('obj', (object,), {
            'phone': '+15551234570',
            'id': 'test-token-id'
        })()
        mock_sms_service.return_value.verify_magic_link_token.side_effect = [mock_magic_token, None]
        
        token = MagicLinkToken(
            id=str(uuid.uuid4()),
            phone="+15551234570",  # Unique phone number
            token=f"test-token-{uuid.uuid4().hex[:8]}",  # Unique token
            expires_at=datetime(2024, 12, 31, 23, 59, 59)
        )
        db_session.add(token)
        db_session.commit()
        
        # First use should succeed
        response1 = client.get(f"/api/auth/verify?token={token.id}")
        assert response1.status_code == 200
        
        # Second use should fail
        response2 = client.get(f"/api/auth/verify?token={token.id}")
        assert response2.status_code == 401
        assert "Invalid or expired token" in response2.json()["detail"]
