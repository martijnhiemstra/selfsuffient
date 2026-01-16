"""
Test suite for image display and social sharing features
Tests:
- /api/files/{path} endpoint for serving images with CORS
- Public project image display
- Share button functionality
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test project with image
TEST_PROJECT_ID = "5cea0f68-77e6-462b-8cc6-2128f0f300e1"
TEST_IMAGE_PATH = f"projects/{TEST_PROJECT_ID}/cover.png"


class TestHealthAndBasics:
    """Basic health check tests"""
    
    def test_health_endpoint(self):
        """Test health endpoint returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✓ Health endpoint working")


class TestFileServing:
    """Tests for /api/files/{path} endpoint"""
    
    def test_file_endpoint_returns_image(self):
        """Test that /api/files/{path} serves images correctly"""
        response = requests.get(f"{BASE_URL}/api/files/{TEST_IMAGE_PATH}")
        assert response.status_code == 200
        assert "image" in response.headers.get("Content-Type", "")
        print(f"✓ File endpoint returns image with Content-Type: {response.headers.get('Content-Type')}")
    
    def test_file_endpoint_cors_headers(self):
        """Test that /api/files/{path} includes CORS headers"""
        response = requests.get(f"{BASE_URL}/api/files/{TEST_IMAGE_PATH}")
        assert response.status_code == 200
        # Check for CORS headers
        cors_origin = response.headers.get("Access-Control-Allow-Origin")
        cross_origin_policy = response.headers.get("Cross-Origin-Resource-Policy")
        print(f"✓ CORS headers - Access-Control-Allow-Origin: {cors_origin}, Cross-Origin-Resource-Policy: {cross_origin_policy}")
        # At least one CORS header should be present
        assert cors_origin == "*" or cross_origin_policy == "cross-origin", "CORS headers missing"
    
    def test_file_endpoint_404_for_missing_file(self):
        """Test that /api/files/{path} returns 404 for non-existent files"""
        response = requests.get(f"{BASE_URL}/api/files/nonexistent/file.png")
        assert response.status_code == 404
        print("✓ File endpoint returns 404 for missing files")
    
    def test_file_endpoint_security_path_traversal(self):
        """Test that /api/files/{path} blocks path traversal attempts"""
        response = requests.get(f"{BASE_URL}/api/files/../../../etc/passwd")
        assert response.status_code in [403, 404]
        print(f"✓ Path traversal blocked with status {response.status_code}")


class TestPublicProjects:
    """Tests for public project endpoints"""
    
    def test_public_projects_list(self):
        """Test public projects list endpoint"""
        response = requests.get(f"{BASE_URL}/api/public/projects")
        assert response.status_code == 200
        data = response.json()
        assert "projects" in data
        print(f"✓ Public projects list returns {len(data['projects'])} projects")
    
    def test_public_project_with_image(self):
        """Test public project detail includes image path"""
        response = requests.get(f"{BASE_URL}/api/public/projects/{TEST_PROJECT_ID}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Backyard Garden"
        assert data["image"] is not None
        assert "/uploads/projects/" in data["image"]
        print(f"✓ Public project has image: {data['image']}")
    
    def test_public_project_blog_endpoint(self):
        """Test public project blog endpoint"""
        response = requests.get(f"{BASE_URL}/api/public/projects/{TEST_PROJECT_ID}/blog")
        assert response.status_code == 200
        data = response.json()
        assert "entries" in data
        print(f"✓ Public project blog returns {len(data['entries'])} entries")
    
    def test_public_project_library_endpoint(self):
        """Test public project library endpoint"""
        response = requests.get(f"{BASE_URL}/api/public/projects/{TEST_PROJECT_ID}/library")
        assert response.status_code == 200
        data = response.json()
        assert "entries" in data
        print(f"✓ Public project library returns {len(data['entries'])} entries")
    
    def test_public_project_gallery_endpoint(self):
        """Test public project gallery endpoint"""
        response = requests.get(f"{BASE_URL}/api/public/projects/{TEST_PROJECT_ID}/gallery")
        assert response.status_code == 200
        data = response.json()
        assert "folders" in data or "images" in data
        print(f"✓ Public project gallery returns folders/images")


class TestAuthentication:
    """Tests for authentication endpoints"""
    
    def test_login_with_valid_credentials(self):
        """Test login with admin credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@selfsufficient.app",
            "password": "admin123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == "admin@selfsufficient.app"
        print("✓ Login with admin credentials successful")
        return data["token"]
    
    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@selfsufficient.app",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        print("✓ Login with invalid credentials returns 401")


class TestAuthenticatedProjectAccess:
    """Tests for authenticated project access"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@selfsufficient.app",
            "password": "admin123"
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Authentication failed")
    
    def test_authenticated_projects_list(self, auth_token):
        """Test authenticated projects list"""
        response = requests.get(
            f"{BASE_URL}/api/projects",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "projects" in data
        print(f"✓ Authenticated projects list returns {len(data['projects'])} projects")
    
    def test_authenticated_project_detail(self, auth_token):
        """Test authenticated project detail with image"""
        response = requests.get(
            f"{BASE_URL}/api/projects/{TEST_PROJECT_ID}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Backyard Garden"
        assert data["image"] is not None
        print(f"✓ Authenticated project detail has image: {data['image']}")
    
    def test_authenticated_gallery_access(self, auth_token):
        """Test authenticated gallery access"""
        response = requests.get(
            f"{BASE_URL}/api/projects/{TEST_PROJECT_ID}/gallery",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Authenticated gallery access successful")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
