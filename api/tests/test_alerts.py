"""
Unit tests for alert CRUD operations
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import json

class TestAlerts:
    """Test alert CRUD operations"""
    
    def test_create_alert_success(self, client, auth_headers, test_user):
        """Test successful alert creation"""
        with patch('middleware.auth.get_current_user', return_value=test_user):
            alert_data = {
                "park": "Magic Kingdom",
                "restaurant": "Cinderella's Royal Table",
                "date": "2024-12-25T00:00:00",
                "time_start": "18:00",
                "time_end": "20:00",
                "party_size": 4,
                "channels": {"email": True, "sms": True}
            }
            
            response = client.post("/api/alerts", json=alert_data, headers=auth_headers)
            assert response.status_code == 201
            assert response.json()["restaurant"] == alert_data["restaurant"]
            assert response.json()["user_id"] == test_user.id
    
    def test_create_alert_invalid_data(self, client, auth_headers, test_user):
        """Test alert creation with invalid data"""
        with patch('deps.get_current_active_user', return_value=test_user):
            invalid_data = {
                "restaurant": "",  # Empty restaurant
                "date": "invalid-date",  # Invalid date
                "time_start": "25:00",  # Invalid time
                "party_size": -1  # Invalid party size
            }
            
            response = client.post("/api/alerts", json=invalid_data, headers=auth_headers)
            assert response.status_code == 422  # Validation error
    
    def test_create_alert_unauthorized(self, client):
        """Test alert creation without authentication"""
        alert_data = {
            "park": "Magic Kingdom",
            "restaurant": "Cinderella's Royal Table",
            "date": "2024-12-25T00:00:00",
            "time_start": "18:00",
            "time_end": "20:00",
            "party_size": 4
        }
        
        response = client.post("/api/alerts", json=alert_data)
        assert response.status_code == 403  # FastAPI HTTPBearer returns 403 for missing token
    
    def test_get_alerts_success(self, client, auth_headers, test_user, test_alert):
        """Test getting user's alerts"""
        with patch('middleware.auth.get_current_user', return_value=test_user):
            response = client.get("/api/alerts", headers=auth_headers)
            assert response.status_code == 200
            alerts = response.json()
            assert len(alerts) >= 1
            assert any(alert["id"] == test_alert.id for alert in alerts)
    
    def test_get_alerts_unauthorized(self, client):
        """Test getting alerts without authentication"""
        response = client.get("/api/alerts")
        assert response.status_code == 403  # FastAPI HTTPBearer returns 403 for missing token
    
    def test_get_alert_by_id_success(self, client, auth_headers, test_user, test_alert):
        """Test getting specific alert by ID"""
        with patch('deps.get_current_active_user', return_value=test_user):
            response = client.get(f"/api/alerts/{test_alert.id}", headers=auth_headers)
            assert response.status_code == 200
            assert response.json()["id"] == test_alert.id
    
    def test_get_alert_by_id_not_found(self, client, auth_headers, test_user):
        """Test getting non-existent alert"""
        with patch('deps.get_current_active_user', return_value=test_user):
            fake_id = "00000000-0000-0000-0000-000000000000"
            response = client.get(f"/api/alerts/{fake_id}", headers=auth_headers)
            assert response.status_code == 404
    
    def test_get_alert_by_id_unauthorized(self, client, test_alert):
        """Test getting alert without authentication"""
        response = client.get(f"/api/alerts/{test_alert.id}")
        assert response.status_code == 403  # FastAPI HTTPBearer returns 403 for missing token
    
    def test_update_alert_success(self, client, auth_headers, test_user, test_alert):
        """Test successful alert update"""
        with patch('deps.get_current_active_user', return_value=test_user):
            update_data = {
                "party_size": 6,
                "time_start": "19:00",
                "status": "paused"
            }
            
            response = client.patch(f"/api/alerts/{test_alert.id}", json=update_data, headers=auth_headers)
            assert response.status_code == 200
            assert response.json()["party_size"] == 6
            assert response.json()["time_start"] == "19:00"
            assert response.json()["status"] == "paused"
    
    def test_update_alert_invalid_data(self, client, auth_headers, test_user, test_alert):
        """Test alert update with invalid data"""
        with patch('deps.get_current_active_user', return_value=test_user):
            invalid_data = {
                "party_size": -1,  # Invalid party size
                "time_start": "25:00"  # Invalid time
            }
            
            response = client.patch(f"/api/alerts/{test_alert.id}", json=invalid_data, headers=auth_headers)
            assert response.status_code == 422  # Validation error
    
    def test_update_alert_not_found(self, client, auth_headers, test_user):
        """Test updating non-existent alert"""
        with patch('deps.get_current_active_user', return_value=test_user):
            fake_id = "00000000-0000-0000-0000-000000000000"
            update_data = {"party_size": 6}
            
            response = client.patch(f"/api/alerts/{fake_id}", json=update_data, headers=auth_headers)
            assert response.status_code == 404
    
    def test_delete_alert_success(self, client, auth_headers, test_user, test_alert):
        """Test successful alert deletion"""
        with patch('deps.get_current_active_user', return_value=test_user):
            response = client.delete(f"/api/alerts/{test_alert.id}", headers=auth_headers)
            assert response.status_code == 204  # No Content for successful deletion
    
    def test_delete_alert_not_found(self, client, auth_headers, test_user):
        """Test deleting non-existent alert"""
        with patch('deps.get_current_active_user', return_value=test_user):
            fake_id = "00000000-0000-0000-0000-000000000000"
            response = client.delete(f"/api/alerts/{fake_id}", headers=auth_headers)
            assert response.status_code == 404
    
    def test_delete_alert_unauthorized(self, client, test_alert):
        """Test deleting alert without authentication"""
        response = client.delete(f"/api/alerts/{test_alert.id}")
        assert response.status_code == 403  # FastAPI HTTPBearer returns 403 for missing token
    
    def test_get_alerts_with_pagination(self, client, auth_headers, test_user, db_session):
        """Test getting alerts with pagination"""
        with patch('deps.get_current_active_user', return_value=test_user):
            # Create multiple alerts
            from models.alert import Alert
            import uuid
            
            from datetime import datetime
            
            for i in range(5):
                alert = Alert(
                    id=str(uuid.uuid4()),
                    user_id=test_user.id,
                    park="Magic Kingdom",
                    restaurant=f"Restaurant {i}",
                    date=datetime(2024, 12, 25),
                    time_start="18:00",
                    time_end="20:00",
                    party_size=4,
                    status="active"
                )
                db_session.add(alert)
            db_session.commit()
            
            # Test pagination
            response = client.get("/api/alerts?limit=3&offset=0", headers=auth_headers)
            assert response.status_code == 200
            alerts = response.json()
            assert len(alerts) <= 3
    
    def test_get_alerts_with_filtering(self, client, auth_headers, test_user, test_alert):
        """Test getting alerts with status filtering"""
        with patch('deps.get_current_active_user', return_value=test_user):
            # Test filtering by status
            response = client.get("/api/alerts?status=active", headers=auth_headers)
            assert response.status_code == 200
            alerts = response.json()
            assert all(alert["status"] == "active" for alert in alerts)
    
    def test_alert_ownership(self, client, auth_headers, test_user, db_session):
        """Test that users can only access their own alerts"""
        # Create another user and alert
        from models.user import User
        from models.alert import Alert
        import uuid
        
        other_user = User(
            id=str(uuid.uuid4()),
            email="other@mousealerts.com",
            phone="+15551234568",
            plan="free",
            subscription_status="active"
        )
        db_session.add(other_user)
        db_session.commit()
        
        from datetime import datetime
        
        other_alert = Alert(
            id=str(uuid.uuid4()),
            user_id=other_user.id,
            park="Magic Kingdom",
            restaurant="Other Restaurant",
            date=datetime(2024, 12, 25),
            time_start="18:00",
            time_end="20:00",
            party_size=4,
            status="active"
        )
        db_session.add(other_alert)
        db_session.commit()
        
        with patch('deps.get_current_active_user', return_value=test_user):
            # Try to access other user's alert
            response = client.get(f"/api/alerts/{other_alert.id}", headers=auth_headers)
            assert response.status_code == 404  # Should not find other user's alert
    
    def test_alert_statistics(self, client, auth_headers, test_user, test_alert):
        """Test getting alert statistics"""
        # Ensure the test_alert is associated with the test_user
        test_alert.user_id = test_user.id
        
        with patch('deps.get_current_active_user', return_value=test_user):
            response = client.get("/api/alerts/stats", headers=auth_headers)
            assert response.status_code == 200
            stats = response.json()
            assert "total_alerts" in stats
            assert "active_alerts" in stats
            assert "paused_alerts" in stats
            assert "expired_alerts" in stats
