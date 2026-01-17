"""
Test file for:
1. CORS fix for project image upload
2. Max upload size (5MB) validation on backend
3. /api/config endpoint returning max_upload_size_mb and max_upload_size_bytes
"""
import pytest
import requests
import os
import io

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "admin@selfsufficient.app"
TEST_PASSWORD = "admin123"

# Test project ID provided in the review request
TEST_PROJECT_ID = "501bdf7c-900b-4af9-b615-e612dbfa7789"


class TestConfigEndpoint:
    """Test /api/config endpoint returns upload size configuration"""
    
    def test_config_endpoint_returns_max_upload_size(self):
        """Test that /api/config returns max_upload_size_mb and max_upload_size_bytes"""
        response = requests.get(f"{BASE_URL}/api/config")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "max_upload_size_mb" in data, "max_upload_size_mb not in response"
        assert "max_upload_size_bytes" in data, "max_upload_size_bytes not in response"
        assert "allowed_image_types" in data, "allowed_image_types not in response"
        
        # Verify values
        assert data["max_upload_size_mb"] == 5, f"Expected 5MB, got {data['max_upload_size_mb']}"
        assert data["max_upload_size_bytes"] == 5 * 1024 * 1024, f"Expected {5*1024*1024}, got {data['max_upload_size_bytes']}"
        assert isinstance(data["allowed_image_types"], list), "allowed_image_types should be a list"
        assert "image/jpeg" in data["allowed_image_types"], "image/jpeg should be allowed"
        print("✓ /api/config returns correct max upload size configuration")


class TestCORSHeaders:
    """Test CORS headers are properly set on responses"""
    
    def test_cors_headers_on_health_endpoint(self):
        """Test CORS headers on health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        
        # Check CORS headers
        assert "access-control-allow-origin" in response.headers or "Access-Control-Allow-Origin" in response.headers, \
            "Missing Access-Control-Allow-Origin header"
        print("✓ CORS headers present on /api/health")
    
    def test_cors_headers_on_config_endpoint(self):
        """Test CORS headers on config endpoint"""
        response = requests.get(f"{BASE_URL}/api/config")
        assert response.status_code == 200
        
        # Check CORS headers (case-insensitive)
        headers_lower = {k.lower(): v for k, v in response.headers.items()}
        assert "access-control-allow-origin" in headers_lower, "Missing Access-Control-Allow-Origin header"
        print("✓ CORS headers present on /api/config")
    
    def test_cors_preflight_options_request(self):
        """Test OPTIONS preflight request returns proper CORS headers"""
        response = requests.options(f"{BASE_URL}/api/health")
        
        headers_lower = {k.lower(): v for k, v in response.headers.items()}
        assert "access-control-allow-origin" in headers_lower, "Missing Access-Control-Allow-Origin on OPTIONS"
        assert "access-control-allow-methods" in headers_lower, "Missing Access-Control-Allow-Methods on OPTIONS"
        print("✓ CORS preflight OPTIONS request returns proper headers")


class TestUploadSizeValidation:
    """Test backend validates file size and returns 413 for files > 5MB"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip(f"Authentication failed: {response.status_code} - {response.text}")
    
    def test_login_works(self, auth_token):
        """Verify login works with test credentials"""
        assert auth_token is not None, "Failed to get auth token"
        print(f"✓ Login successful, got token: {auth_token[:20]}...")
    
    def test_project_image_upload_small_file(self, auth_token):
        """Test uploading a small valid image to project"""
        # Create a small test image (1x1 pixel PNG)
        # PNG header for a 1x1 transparent pixel
        small_png = bytes([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
            0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
            0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,  # 1x1 dimensions
            0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4,  # bit depth, color type, etc
            0x89, 0x00, 0x00, 0x00, 0x0A, 0x49, 0x44, 0x41,  # IDAT chunk
            0x54, 0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00,  # compressed data
            0x05, 0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4, 0x00,  # more data
            0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44,  # IEND chunk
            0xAE, 0x42, 0x60, 0x82
        ])
        
        files = {'file': ('test_small.png', io.BytesIO(small_png), 'image/png')}
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        response = requests.post(
            f"{BASE_URL}/api/projects/{TEST_PROJECT_ID}/image",
            files=files,
            headers=headers
        )
        
        # Should succeed (200) or project not found (404) if test project doesn't exist
        assert response.status_code in [200, 404], f"Unexpected status: {response.status_code} - {response.text}"
        if response.status_code == 200:
            print("✓ Small image upload succeeded")
        else:
            print(f"✓ Project {TEST_PROJECT_ID} not found (expected if test project doesn't exist)")
    
    def test_project_image_upload_large_file_returns_413(self, auth_token):
        """Test uploading a file > 5MB returns 413 error"""
        # Create a file larger than 5MB (5.5MB)
        large_content = b'x' * (6 * 1024 * 1024)  # 6MB of data
        
        files = {'file': ('test_large.jpg', io.BytesIO(large_content), 'image/jpeg')}
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        response = requests.post(
            f"{BASE_URL}/api/projects/{TEST_PROJECT_ID}/image",
            files=files,
            headers=headers
        )
        
        # Should return 413 for file too large, or 404 if project doesn't exist
        if response.status_code == 404:
            print(f"✓ Project {TEST_PROJECT_ID} not found - skipping large file test")
            return
        
        assert response.status_code == 413, f"Expected 413 for large file, got {response.status_code} - {response.text}"
        
        # Verify error message mentions file size
        data = response.json()
        assert "detail" in data, "Response should have detail field"
        assert "5MB" in data["detail"] or "too large" in data["detail"].lower(), \
            f"Error message should mention size limit: {data['detail']}"
        print("✓ Large file upload correctly returns 413 with size limit message")
    
    def test_gallery_image_upload_large_file_returns_413(self, auth_token):
        """Test gallery image upload with large file returns 413"""
        # Create a file larger than 5MB
        large_content = b'x' * (6 * 1024 * 1024)  # 6MB
        
        files = {'file': ('test_large.jpg', io.BytesIO(large_content), 'image/jpeg')}
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        response = requests.post(
            f"{BASE_URL}/api/projects/{TEST_PROJECT_ID}/gallery/images",
            files=files,
            headers=headers
        )
        
        # Should return 413 for file too large, or 404 if project doesn't exist
        if response.status_code == 404:
            print(f"✓ Project {TEST_PROJECT_ID} not found - skipping gallery large file test")
            return
        
        assert response.status_code == 413, f"Expected 413 for large file, got {response.status_code}"
        print("✓ Gallery large file upload correctly returns 413")


class TestCORSWithOriginHeader:
    """Test CORS with Origin header (simulating cross-origin request)"""
    
    def test_cors_with_origin_header(self):
        """Test that requests with Origin header get proper CORS response"""
        headers = {
            'Origin': 'https://app.earthly-life.eu'
        }
        response = requests.get(f"{BASE_URL}/api/health", headers=headers)
        assert response.status_code == 200
        
        headers_lower = {k.lower(): v for k, v in response.headers.items()}
        assert "access-control-allow-origin" in headers_lower, "Missing CORS header with Origin"
        print("✓ CORS headers present when Origin header is sent")
    
    def test_cors_on_files_endpoint(self):
        """Test CORS headers on /api/files endpoint"""
        # Try to access a file (may not exist, but should still have CORS headers)
        headers = {
            'Origin': 'https://app.earthly-life.eu'
        }
        response = requests.get(f"{BASE_URL}/api/files/test.png", headers=headers)
        
        # Even 404 should have CORS headers
        headers_lower = {k.lower(): v for k, v in response.headers.items()}
        assert "access-control-allow-origin" in headers_lower, "Missing CORS header on /api/files"
        print("✓ CORS headers present on /api/files endpoint")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
