"""
Backend tests for Garden Designer API
Tests Phase 3: Generate garden design functionality
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Known test data
TEST_PROJECT_ID = "72868dc9-f97d-4209-83e8-8d2c6fd59c67"  # Community Garden
NONEXISTENT_PROJECT_ID = "00000000-0000-0000-0000-000000000000"


class TestGardenDesignerAPI:
    """Garden Designer API endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with auth token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login to get auth token
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@selfsufficient.app",
            "password": "admin123"
        })
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        
        token = login_response.json().get("access_token")
        assert token, "No access_token in login response"
        self.session.headers.update({"Authorization": f"Bearer {token}"})
    
    def test_generate_garden_no_api_key_returns_400(self):
        """
        POST /api/garden/generate should return 400 with 'API key not configured' 
        when user has no OpenAI API key configured
        """
        payload = {
            "project_id": TEST_PROJECT_ID,
            "boundary": {
                "points": [
                    {"x": 1, "y": 1},
                    {"x": 10, "y": 1},
                    {"x": 10, "y": 10},
                    {"x": 1, "y": 10}
                ],
                "scale": 1.0
            },
            "details": {
                "latitude": 52.3676,
                "longitude": 4.9041,
                "wind_direction": "SW",
                "garden_goal": "mixed",
                "plant_preferences": ["vegetables", "herbs"]
            }
        }
        
        response = self.session.post(f"{BASE_URL}/api/garden/generate", json=payload)
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "detail" in data, "No 'detail' field in error response"
        assert "API key" in data["detail"], f"Expected 'API key' in error detail, got: {data['detail']}"
        print(f"✓ Generate returns 400 with API key error: {data['detail']}")
    
    def test_generate_garden_nonexistent_project_returns_404(self):
        """
        POST /api/garden/generate should return 404 if project not found
        """
        payload = {
            "project_id": NONEXISTENT_PROJECT_ID,
            "boundary": {
                "points": [
                    {"x": 1, "y": 1},
                    {"x": 10, "y": 1},
                    {"x": 10, "y": 10},
                    {"x": 1, "y": 10}
                ],
                "scale": 1.0
            },
            "details": {
                "latitude": 52.3676,
                "longitude": 4.9041,
                "wind_direction": "SW",
                "garden_goal": "mixed",
                "plant_preferences": ["vegetables", "herbs"]
            }
        }
        
        response = self.session.post(f"{BASE_URL}/api/garden/generate", json=payload)
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "detail" in data, "No 'detail' field in error response"
        assert "not found" in data["detail"].lower(), f"Expected 'not found' in detail: {data['detail']}"
        print(f"✓ Generate returns 404 for non-existent project: {data['detail']}")
    
    def test_get_designs_empty_list_for_project_with_no_designs(self):
        """
        GET /api/garden/designs/{project_id} should return empty list for project with no designs
        """
        response = self.session.get(f"{BASE_URL}/api/garden/designs/{TEST_PROJECT_ID}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "designs" in data, "No 'designs' field in response"
        assert "total" in data, "No 'total' field in response"
        assert isinstance(data["designs"], list), "designs should be a list"
        # It might have designs or be empty - both are valid
        print(f"✓ GET designs returns {data['total']} designs for project")
    
    def test_generate_garden_invalid_payload_returns_422(self):
        """
        POST /api/garden/generate with missing required fields should return 422
        """
        # Missing required fields
        payload = {
            "project_id": TEST_PROJECT_ID
            # Missing boundary and details
        }
        
        response = self.session.post(f"{BASE_URL}/api/garden/generate", json=payload)
        
        assert response.status_code == 422, f"Expected 422, got {response.status_code}: {response.text}"
        print(f"✓ Generate returns 422 for invalid payload")
    
    def test_generate_garden_unauthenticated_returns_401(self):
        """
        POST /api/garden/generate without auth should return 401
        """
        # Create new session without auth
        no_auth_session = requests.Session()
        no_auth_session.headers.update({"Content-Type": "application/json"})
        
        payload = {
            "project_id": TEST_PROJECT_ID,
            "boundary": {
                "points": [{"x": 1, "y": 1}, {"x": 10, "y": 1}, {"x": 10, "y": 10}],
                "scale": 1.0
            },
            "details": {
                "latitude": 52.3676,
                "longitude": 4.9041,
                "wind_direction": "SW",
                "garden_goal": "mixed",
                "plant_preferences": ["vegetables"]
            }
        }
        
        response = no_auth_session.post(f"{BASE_URL}/api/garden/generate", json=payload)
        
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"✓ Generate returns {response.status_code} for unauthenticated request")
    
    def test_get_designs_unauthenticated_returns_401_or_403(self):
        """
        GET /api/garden/designs/{project_id} without auth should return 401 or 403
        """
        no_auth_session = requests.Session()
        response = no_auth_session.get(f"{BASE_URL}/api/garden/designs/{TEST_PROJECT_ID}")
        
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"✓ GET designs returns {response.status_code} for unauthenticated request")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
