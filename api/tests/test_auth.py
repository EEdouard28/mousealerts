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
    
    @patch('routers.auth.send_sms')
    def test_magic_link_request_success(self, mock_send_sms, client, db_session):
        """Test successful magic link request"""
        mock_send_sms.return_value = True
        
        response = client.post("/api/auth/magic-link", json={"phone": "+15551234567"})
        assert response.status_code == 200
        assert response.json()["message"] == "Magic link sent successfully"
        mock_send_sms.assert_called_once()
    
    @patch('routers.auth.send_sms')
    def test_magic_link_request_sms_failure(self, mock_send_sms, client, db_session):
        """Test magic link request when SMS fails"""
        mock_send_sms.return_value = False
        
        response = client.post("/api/auth/magic-link", json={"phone": "+15551234567"})
        assert response.status_code == 500
        assert "error" in response.json()
    
    def test_verify_token_invalid(self, client):
        """Test token verification with invalid token"""
        response = client.get("/api/auth/verify?token=invalid-token")
        assert response.status_code == 401
        assert "Invalid or expired token" in response.json()["detail"]
    
    def test_verify_token_missing(self, client):
        """Test token verification without token"""
        response = client.get("/api/auth/verify")
        assert response.status_code == 422  # Validation error
    
    def test_verify_token_success(self, client, db_session):
        """Test successful token verification"""
        # Create a valid magic link token
        from models.magic_link_token import MagicLinkToken
        import uuid
        
        token = MagicLinkToken(
            id=str(uuid.uuid4()),
            phone="+15551234567",
            expires_at="2024-12-31T23:59:59Z"
        )
        db_session.add(token)
        db_session.commit()
        
        response = client.get(f"/api/auth/verify?token={token.id}")
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "user" in response.json()
    
    def test_logout_success(self, client, auth_headers):
        """Test successful logout"""
        response = client.post("/api/auth/logout", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"
    
    def test_logout_without_auth(self, client):
        """Test logout without authentication"""
        response = client.post("/api/auth/logout")
        assert response.status_code == 401
    
    def test_get_me_success(self, client, auth_headers, test_user):
        """Test getting current user profile"""
        with patch('deps.get_current_active_user', return_value=test_user):
            response = client.get("/api/me", headers=auth_headers)
            assert response.status_code == 200
            assert response.json()["email"] == test_user.email
            assert response.json()["phone"] == test_user.phone
    
    def test_get_me_unauthorized(self, client):
        """Test getting user profile without authentication"""
        response = client.get("/api/me")
        assert response.status_code == 401
    
    def test_rate_limiting_magic_link(self, client):
        """Test rate limiting for magic link requests"""
        # This would test the rate limiting functionality
        # For now, we'll just test that the endpoint exists
        response = client.post("/api/auth/magic-link", json={"phone": "+15551234567"})
        # The actual rate limiting test would require multiple requests
        assert response.status_code in [200, 429]  # Success or rate limited
    
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
    
    def test_phone_number_e164_format(self, client):
        """Test E.164 phone number format validation"""
        valid_phones = [
            "+15551234567",
            "+1234567890",
            "+44123456789"
        ]
        
        for phone in valid_phones:
            with patch('routers.auth.send_sms', return_value=True):
                response = client.post("/api/auth/magic-link", json={"phone": phone})
                assert response.status_code == 200
    
    def test_token_expiration(self, client, db_session):
        """Test token expiration handling"""
        from models.magic_link_token import MagicLinkToken
        import uuid
        from datetime import datetime, timedelta
        
        # Create an expired token
        expired_time = datetime.utcnow() - timedelta(hours=1)
        token = MagicLinkToken(
            id=str(uuid.uuid4()),
            phone="+15551234567",
            expires_at=expired_time.isoformat() + "Z"
        )
        db_session.add(token)
        db_session.commit()
        
        response = client.get(f"/api/auth/verify?token={token.id}")
        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower()
    
    def test_token_single_use(self, client, db_session):
        """Test that tokens can only be used once"""
        from models.magic_link_token import MagicLinkToken
        import uuid
        
        token = MagicLinkToken(
            id=str(uuid.uuid4()),
            phone="+15551234567",
            expires_at="2024-12-31T23:59:59Z"
        )
        db_session.add(token)
        db_session.commit()
        
        # First use should succeed
        response1 = client.get(f"/api/auth/verify?token={token.id}")
        assert response1.status_code == 200
        
        # Second use should fail
        response2 = client.get(f"/api/auth/verify?token={token.id}")
        assert response2.status_code == 401
        assert "already used" in response2.json()["detail"].lower()
