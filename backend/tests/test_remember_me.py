"""
Test cases for 'Stay logged in' (remember_me) feature.
Tests JWT token expiry: 24h (default) vs 14 days (remember_me=true)
"""
import pytest
import requests
import jwt
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "admin@selfsufficient.app"
TEST_PASSWORD = "admin123"


class TestRememberMeFeature:
    """Tests for remember_me login functionality"""

    def test_login_without_remember_me_defaults_to_24h(self):
        """Login without remember_me field should default to 24h expiry (backward compat)"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
            # No remember_me field - should default to False
        })
        
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "Response missing access_token"
        
        # Decode token without verification to check expiry
        token = data["access_token"]
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        exp = decoded.get("exp")
        iat = decoded.get("iat")
        assert exp is not None, "Token missing exp claim"
        assert iat is not None, "Token missing iat claim"
        
        # 24 hours = 86400 seconds
        expiry_seconds = exp - iat
        assert expiry_seconds == 86400, f"Expected 24h (86400s) expiry, got {expiry_seconds}s"
        print(f"PASS: Login without remember_me defaults to 24h expiry ({expiry_seconds}s)")

    def test_login_with_remember_me_false_returns_24h(self):
        """Login with remember_me=false should return 24h expiry token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "remember_me": False
        })
        
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "Response missing access_token"
        
        # Decode token without verification
        token = data["access_token"]
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        exp = decoded.get("exp")
        iat = decoded.get("iat")
        assert exp is not None, "Token missing exp claim"
        assert iat is not None, "Token missing iat claim"
        
        # 24 hours = 86400 seconds
        expiry_seconds = exp - iat
        assert expiry_seconds == 86400, f"Expected 24h (86400s) expiry, got {expiry_seconds}s"
        print(f"PASS: Login with remember_me=false returns 24h expiry ({expiry_seconds}s)")

    def test_login_with_remember_me_true_returns_14_days(self):
        """Login with remember_me=true should return 14-day (336h) expiry token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "remember_me": True
        })
        
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "Response missing access_token"
        
        # Decode token without verification
        token = data["access_token"]
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        exp = decoded.get("exp")
        iat = decoded.get("iat")
        assert exp is not None, "Token missing exp claim"
        assert iat is not None, "Token missing iat claim"
        
        # 14 days = 14 * 24 * 3600 = 1209600 seconds
        expiry_seconds = exp - iat
        assert expiry_seconds == 1209600, f"Expected 14 days (1209600s) expiry, got {expiry_seconds}s"
        print(f"PASS: Login with remember_me=true returns 14-day expiry ({expiry_seconds}s)")

    def test_token_is_valid_and_works(self):
        """Verify the token actually works for authenticated requests"""
        # Login with remember_me=true
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "remember_me": True
        })
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Use token to access protected endpoint
        me_response = requests.get(f"{BASE_URL}/api/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        
        assert me_response.status_code == 200, f"Token not valid: {me_response.text}"
        user_data = me_response.json()
        assert user_data["email"] == TEST_EMAIL
        print(f"PASS: Token is valid and works for authenticated requests")

    def test_login_response_structure(self):
        """Verify login response has correct structure"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "remember_me": False
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "access_token" in data, "Missing access_token"
        assert "token_type" in data, "Missing token_type"
        assert "user" in data, "Missing user object"
        
        # Check user object structure
        user = data["user"]
        assert "id" in user, "User missing id"
        assert "email" in user, "User missing email"
        assert "name" in user, "User missing name"
        assert user["email"] == TEST_EMAIL
        
        print(f"PASS: Login response has correct structure")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
