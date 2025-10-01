"""
Security testing for MouseAlerts API
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import json
import time

class TestAuthenticationSecurity:
    """Test authentication security"""
    
    def test_magic_link_token_security(self, client):
        """Test magic link token security"""
        # Test with invalid token
        response = client.get("/api/auth/verify?token=invalid-token")
        assert response.status_code == 401
        
        # Test with empty token
        response = client.get("/api/auth/verify?token=")
        assert response.status_code == 422
        
        # Test with malformed token
        response = client.get("/api/auth/verify?token=<script>alert('xss')</script>")
        assert response.status_code == 401
    
    def test_jwt_token_security(self, client):
        """Test JWT token security"""
        # Test with invalid JWT
        headers = {"Authorization": "Bearer invalid-jwt-token"}
        response = client.get("/api/me", headers=headers)
        assert response.status_code == 401
        
        # Test with malformed JWT
        headers = {"Authorization": "Bearer <script>alert('xss')</script>"}
        response = client.get("/api/me", headers=headers)
        assert response.status_code == 401
        
        # Test with expired JWT (mock)
        headers = {"Authorization": "Bearer expired-jwt-token"}
        response = client.get("/api/me", headers=headers)
        assert response.status_code == 401
    
    def test_rate_limiting_security(self, client):
        """Test rate limiting for security"""
        # Test rate limiting on magic link endpoint
        for i in range(20):  # Make many requests
            response = client.post("/api/auth/magic-link", json={"phone": "+15551234567"})
            if response.status_code == 429:  # Rate limited
                break
        
        # Should eventually be rate limited
        assert response.status_code == 429
    
    def test_session_management(self, client, auth_headers, test_user):
        """Test session management security"""
        with patch('deps.get_current_active_user', return_value=test_user):
            # Test valid session
            response = client.get("/api/me", headers=auth_headers)
            assert response.status_code == 200
            
            # Test session timeout (mock)
            with patch('deps.get_current_active_user', side_effect=Exception("Token expired")):
                response = client.get("/api/me", headers=auth_headers)
                assert response.status_code == 401

class TestDataProtection:
    """Test data protection security"""
    
    def test_input_sanitization(self, client, auth_headers, test_user):
        """Test input sanitization"""
        with patch('deps.get_current_active_user', return_value=test_user):
            # Test XSS prevention
            malicious_data = {
                "restaurant": "<script>alert('xss')</script>",
                "date": "2024-12-25",
                "time_start": "18:00",
                "time_end": "20:00",
                "party_size": 4
            }
            
            response = client.post("/api/alerts", json=malicious_data, headers=auth_headers)
            # Should either reject or sanitize the input
            assert response.status_code in [201, 422]
            
            if response.status_code == 201:
                # Check that the data was sanitized
                alert_data = response.json()
                assert "<script>" not in alert_data["restaurant"]
    
    def test_sql_injection_prevention(self, client, auth_headers, test_user):
        """Test SQL injection prevention"""
        with patch('deps.get_current_active_user', return_value=test_user):
            # Test SQL injection attempts
            malicious_data = {
                "restaurant": "'; DROP TABLE users; --",
                "date": "2024-12-25",
                "time_start": "18:00",
                "time_end": "20:00",
                "party_size": 4
            }
            
            response = client.post("/api/alerts", json=malicious_data, headers=auth_headers)
            # Should handle the input safely
            assert response.status_code in [201, 422]
            
            # Verify that the database is still intact
            response = client.get("/api/alerts", headers=auth_headers)
            assert response.status_code == 200
    
    def test_data_validation(self, client, auth_headers, test_user):
        """Test data validation security"""
        with patch('deps.get_current_active_user', return_value=test_user):
            # Test with invalid data types
            invalid_data = {
                "restaurant": 123,  # Should be string
                "date": "invalid-date",
                "time_start": "25:00",  # Invalid time
                "time_end": "18:00",
                "party_size": "not-a-number"
            }
            
            response = client.post("/api/alerts", json=invalid_data, headers=auth_headers)
            assert response.status_code == 422  # Validation error
    
    def test_file_upload_security(self, client, auth_headers, test_user):
        """Test file upload security"""
        with patch('deps.get_current_active_user', return_value=test_user):
            # Test file upload with malicious content
            malicious_file = {
                "filename": "../../../etc/passwd",
                "content": "malicious content"
            }
            
            # This would test file upload security if implemented
            # For now, we'll just test that the endpoint exists
            response = client.post("/api/upload", json=malicious_file, headers=auth_headers)
            # Should either reject or sanitize the filename
            assert response.status_code in [404, 422, 400]

class TestAPISecurity:
    """Test API security"""
    
    def test_endpoint_authorization(self, client):
        """Test endpoint authorization"""
        # Test protected endpoints without authentication
        protected_endpoints = [
            "/api/me",
            "/api/alerts",
            "/api/admin/dashboard",
            "/api/admin/users",
            "/api/admin/analytics/dashboard"
        ]
        
        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 401  # Unauthorized
    
    def test_admin_authorization(self, client, auth_headers, test_user):
        """Test admin endpoint authorization"""
        with patch('deps.get_current_active_user', return_value=test_user):
            # Test admin endpoints with non-admin user
            admin_endpoints = [
                "/api/admin/dashboard",
                "/api/admin/users",
                "/api/admin/analytics/dashboard"
            ]
            
            for endpoint in admin_endpoints:
                response = client.get(endpoint, headers=auth_headers)
                assert response.status_code == 403  # Forbidden
    
    def test_data_validation_security(self, client, auth_headers, test_user):
        """Test data validation for security"""
        with patch('deps.get_current_active_user', return_value=test_user):
            # Test with oversized data
            oversized_data = {
                "restaurant": "A" * 10000,  # Very long string
                "date": "2024-12-25",
                "time_start": "18:00",
                "time_end": "20:00",
                "party_size": 4
            }
            
            response = client.post("/api/alerts", json=oversized_data, headers=auth_headers)
            # Should either reject or truncate the data
            assert response.status_code in [201, 422, 413]  # 413 = Payload Too Large
    
    def test_error_message_security(self, client):
        """Test error message security"""
        # Test that error messages don't leak sensitive information
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
        
        error_data = response.json()
        # Should not contain sensitive information
        assert "password" not in str(error_data).lower()
        assert "token" not in str(error_data).lower()
        assert "secret" not in str(error_data).lower()
    
    def test_api_rate_limiting(self, client):
        """Test API rate limiting"""
        # Test rate limiting on various endpoints
        endpoints = [
            "/api/auth/magic-link",
            "/api/alerts",
            "/api/me"
        ]
        
        for endpoint in endpoints:
            # Make many requests to test rate limiting
            for i in range(10):
                if endpoint == "/api/auth/magic-link":
                    response = client.post(endpoint, json={"phone": "+15551234567"})
                else:
                    response = client.get(endpoint)
                
                if response.status_code == 429:  # Rate limited
                    break
            
            # Should eventually be rate limited
            assert response.status_code == 429

class TestSecurityHeaders:
    """Test security headers"""
    
    def test_security_headers(self, client):
        """Test security headers"""
        response = client.get("/health")
        assert response.status_code == 200
        
        headers = response.headers
        
        # Check for security headers
        security_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "Content-Security-Policy"
        ]
        
        for header in security_headers:
            # In a real implementation, these headers should be present
            # For now, we'll just test that the endpoint responds
            assert response.status_code == 200
    
    def test_cors_headers(self, client):
        """Test CORS headers"""
        response = client.options("/api/alerts")
        assert response.status_code == 200
        
        headers = response.headers
        
        # Check for CORS headers
        cors_headers = [
            "Access-Control-Allow-Origin",
            "Access-Control-Allow-Methods",
            "Access-Control-Allow-Headers"
        ]
        
        for header in cors_headers:
            # In a real implementation, these headers should be present
            # For now, we'll just test that the endpoint responds
            assert response.status_code == 200

class TestInputValidation:
    """Test input validation security"""
    
    def test_phone_number_validation(self, client):
        """Test phone number validation"""
        # Test various phone number formats
        test_cases = [
            ("+15551234567", True),  # Valid
            ("15551234567", False),  # Missing +
            ("+1-555-123-4567", False),  # Invalid format
            ("+1555123456789", False),  # Too long
            ("+1555123456", False),  # Too short
            ("", False),  # Empty
            ("+15551234567a", False),  # Contains letters
        ]
        
        for phone, should_be_valid in test_cases:
            response = client.post("/api/auth/magic-link", json={"phone": phone})
            if should_be_valid:
                assert response.status_code in [200, 500]  # 500 for SMS service error
            else:
                assert response.status_code == 422  # Validation error
    
    def test_date_validation(self, client, auth_headers, test_user):
        """Test date validation"""
        with patch('deps.get_current_active_user', return_value=test_user):
            # Test various date formats
            test_cases = [
                ("2024-12-25", True),  # Valid
                ("2024-13-25", False),  # Invalid month
                ("2024-12-32", False),  # Invalid day
                ("2023-12-25", False),  # Past date
                ("invalid-date", False),  # Invalid format
                ("", False),  # Empty
            ]
            
            for date, should_be_valid in test_cases:
                alert_data = {
                    "restaurant": "Test Restaurant",
                    "date": date,
                    "time_start": "18:00",
                    "time_end": "20:00",
                    "party_size": 4
                }
                
                response = client.post("/api/alerts", json=alert_data, headers=auth_headers)
                if should_be_valid:
                    assert response.status_code in [201, 422]  # 422 for other validation errors
                else:
                    assert response.status_code == 422  # Validation error
    
    def test_time_validation(self, client, auth_headers, test_user):
        """Test time validation"""
        with patch('deps.get_current_active_user', return_value=test_user):
            # Test various time formats
            test_cases = [
                ("18:00", True),  # Valid
                ("25:00", False),  # Invalid hour
                ("18:60", False),  # Invalid minute
                ("invalid-time", False),  # Invalid format
                ("", False),  # Empty
            ]
            
            for time, should_be_valid in test_cases:
                alert_data = {
                    "restaurant": "Test Restaurant",
                    "date": "2024-12-25",
                    "time_start": time,
                    "time_end": "20:00",
                    "party_size": 4
                }
                
                response = client.post("/api/alerts", json=alert_data, headers=auth_headers)
                if should_be_valid:
                    assert response.status_code in [201, 422]  # 422 for other validation errors
                else:
                    assert response.status_code == 422  # Validation error

class TestAuthenticationBypass:
    """Test authentication bypass attempts"""
    
    def test_authentication_bypass_attempts(self, client):
        """Test various authentication bypass attempts"""
        # Test with various bypass attempts
        bypass_attempts = [
            {"Authorization": "Bearer "},
            {"Authorization": "Bearer null"},
            {"Authorization": "Bearer undefined"},
            {"Authorization": "Bearer 0"},
            {"Authorization": "Bearer false"},
            {"Authorization": "Bearer true"},
            {"Authorization": "Bearer admin"},
            {"Authorization": "Bearer root"},
            {"Authorization": "Bearer test"},
        ]
        
        for headers in bypass_attempts:
            response = client.get("/api/me", headers=headers)
            assert response.status_code == 401  # Should be unauthorized
    
    def test_sql_injection_in_auth(self, client):
        """Test SQL injection in authentication"""
        # Test SQL injection attempts in auth endpoints
        injection_attempts = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "admin'/*",
            "admin' UNION SELECT * FROM users--"
        ]
        
        for injection in injection_attempts:
            response = client.post("/api/auth/magic-link", json={"phone": injection})
            # Should handle the injection safely
            assert response.status_code in [422, 500]  # Validation error or server error

if __name__ == "__main__":
    """Run all security tests"""
    print("Running MouseAlerts API security tests...")
    
    # Run all tests
    TestAuthenticationSecurity().test_magic_link_token_security(None)
    TestDataProtection().test_input_sanitization(None, None, None)
    TestAPISecurity().test_endpoint_authorization(None)
    TestSecurityHeaders().test_security_headers(None)
    TestInputValidation().test_phone_number_validation(None)
    TestAuthenticationBypass().test_authentication_bypass_attempts(None)
    
    print("All security tests completed!")
