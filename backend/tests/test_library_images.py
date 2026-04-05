"""
Test Library Image Upload/Delete Endpoints
Tests for:
- POST /api/projects/:id/library/entries/:entryId/images - upload image
- DELETE /api/projects/:id/library/entries/:entryId/images/:imageId - delete image
- GET /api/projects/:id/library - returns entries with 'images' array
"""
import pytest
import requests
import os
import io

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
PROJECT_ID = "501bdf7c-900b-4af9-b615-e612dbfa7789"  # TEST_Project_Refactor


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "admin@selfsufficient.app",
        "password": "admin123"
    })
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json().get("access_token")


@pytest.fixture(scope="module")
def api_client(auth_token):
    """Shared requests session with auth"""
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    })
    return session


@pytest.fixture
def test_library_entry(api_client):
    """Create a test library entry for image upload tests"""
    payload = {
        "title": "TEST_Library_Entry_For_Images",
        "description": "Test entry for image upload testing",
        "is_public": False,
        "folder_id": None
    }
    response = api_client.post(f"{BASE_URL}/api/projects/{PROJECT_ID}/library/entries", json=payload)
    assert response.status_code == 200, f"Failed to create library entry: {response.text}"
    entry = response.json()
    yield entry
    # Cleanup: delete the entry after test
    api_client.delete(f"{BASE_URL}/api/projects/{PROJECT_ID}/library/entries/{entry['id']}")


def create_test_image():
    """Create a small test JPEG image in memory"""
    # Create a minimal valid JPEG (1x1 pixel red image)
    # This is a valid JPEG file header + minimal image data
    jpeg_bytes = bytes([
        0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01,
        0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43,
        0x00, 0x08, 0x06, 0x06, 0x07, 0x06, 0x05, 0x08, 0x07, 0x07, 0x07, 0x09,
        0x09, 0x08, 0x0A, 0x0C, 0x14, 0x0D, 0x0C, 0x0B, 0x0B, 0x0C, 0x19, 0x12,
        0x13, 0x0F, 0x14, 0x1D, 0x1A, 0x1F, 0x1E, 0x1D, 0x1A, 0x1C, 0x1C, 0x20,
        0x24, 0x2E, 0x27, 0x20, 0x22, 0x2C, 0x23, 0x1C, 0x1C, 0x28, 0x37, 0x29,
        0x2C, 0x30, 0x31, 0x34, 0x34, 0x34, 0x1F, 0x27, 0x39, 0x3D, 0x38, 0x32,
        0x3C, 0x2E, 0x33, 0x34, 0x32, 0xFF, 0xC0, 0x00, 0x0B, 0x08, 0x00, 0x01,
        0x00, 0x01, 0x01, 0x01, 0x11, 0x00, 0xFF, 0xC4, 0x00, 0x1F, 0x00, 0x00,
        0x01, 0x05, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
        0x09, 0x0A, 0x0B, 0xFF, 0xC4, 0x00, 0xB5, 0x10, 0x00, 0x02, 0x01, 0x03,
        0x03, 0x02, 0x04, 0x03, 0x05, 0x05, 0x04, 0x04, 0x00, 0x00, 0x01, 0x7D,
        0x01, 0x02, 0x03, 0x00, 0x04, 0x11, 0x05, 0x12, 0x21, 0x31, 0x41, 0x06,
        0x13, 0x51, 0x61, 0x07, 0x22, 0x71, 0x14, 0x32, 0x81, 0x91, 0xA1, 0x08,
        0x23, 0x42, 0xB1, 0xC1, 0x15, 0x52, 0xD1, 0xF0, 0x24, 0x33, 0x62, 0x72,
        0x82, 0x09, 0x0A, 0x16, 0x17, 0x18, 0x19, 0x1A, 0x25, 0x26, 0x27, 0x28,
        0x29, 0x2A, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3A, 0x43, 0x44, 0x45,
        0x46, 0x47, 0x48, 0x49, 0x4A, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58, 0x59,
        0x5A, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69, 0x6A, 0x73, 0x74, 0x75,
        0x76, 0x77, 0x78, 0x79, 0x7A, 0x83, 0x84, 0x85, 0x86, 0x87, 0x88, 0x89,
        0x8A, 0x92, 0x93, 0x94, 0x95, 0x96, 0x97, 0x98, 0x99, 0x9A, 0xA2, 0xA3,
        0xA4, 0xA5, 0xA6, 0xA7, 0xA8, 0xA9, 0xAA, 0xB2, 0xB3, 0xB4, 0xB5, 0xB6,
        0xB7, 0xB8, 0xB9, 0xBA, 0xC2, 0xC3, 0xC4, 0xC5, 0xC6, 0xC7, 0xC8, 0xC9,
        0xCA, 0xD2, 0xD3, 0xD4, 0xD5, 0xD6, 0xD7, 0xD8, 0xD9, 0xDA, 0xE1, 0xE2,
        0xE3, 0xE4, 0xE5, 0xE6, 0xE7, 0xE8, 0xE9, 0xEA, 0xF1, 0xF2, 0xF3, 0xF4,
        0xF5, 0xF6, 0xF7, 0xF8, 0xF9, 0xFA, 0xFF, 0xDA, 0x00, 0x08, 0x01, 0x01,
        0x00, 0x00, 0x3F, 0x00, 0xFB, 0xD5, 0xDB, 0x20, 0xA8, 0xF1, 0x7E, 0xDA,
        0xA9, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xD9
    ])
    return io.BytesIO(jpeg_bytes)


class TestLibraryImageEndpoints:
    """Test library image upload and delete endpoints"""

    def test_upload_image_to_library_entry(self, api_client, test_library_entry):
        """Test POST /api/projects/:id/library/entries/:entryId/images"""
        entry_id = test_library_entry["id"]
        
        # Create test image
        image_file = create_test_image()
        files = {
            'file': ('test_image.jpg', image_file, 'image/jpeg')
        }
        
        # Remove Content-Type header for multipart upload
        headers = {"Authorization": api_client.headers["Authorization"]}
        
        response = requests.post(
            f"{BASE_URL}/api/projects/{PROJECT_ID}/library/entries/{entry_id}/images",
            files=files,
            headers=headers
        )
        
        assert response.status_code == 200, f"Upload failed: {response.text}"
        
        data = response.json()
        assert "id" in data, "Response should contain image id"
        assert "url" in data, "Response should contain image url"
        assert "filename" in data, "Response should contain filename"
        assert "entry_id" in data, "Response should contain entry_id"
        assert data["entry_id"] == entry_id, "entry_id should match"
        assert "created_at" in data, "Response should contain created_at"
        
        print(f"✓ Image uploaded successfully: {data['id']}")
        return data

    def test_library_list_includes_images_array(self, api_client, test_library_entry):
        """Test GET /api/projects/:id/library returns entries with 'images' array"""
        entry_id = test_library_entry["id"]
        
        # First upload an image
        image_file = create_test_image()
        files = {'file': ('test_list_image.jpg', image_file, 'image/jpeg')}
        headers = {"Authorization": api_client.headers["Authorization"]}
        
        upload_response = requests.post(
            f"{BASE_URL}/api/projects/{PROJECT_ID}/library/entries/{entry_id}/images",
            files=files,
            headers=headers
        )
        assert upload_response.status_code == 200, f"Upload failed: {upload_response.text}"
        
        # Now fetch library list
        response = api_client.get(f"{BASE_URL}/api/projects/{PROJECT_ID}/library")
        assert response.status_code == 200, f"Library list failed: {response.text}"
        
        data = response.json()
        assert "entries" in data, "Response should contain entries"
        
        # Find our test entry
        test_entry = None
        for entry in data["entries"]:
            if entry["id"] == entry_id:
                test_entry = entry
                break
        
        assert test_entry is not None, "Test entry should be in library list"
        assert "images" in test_entry, "Entry should have 'images' field"
        assert isinstance(test_entry["images"], list), "images should be a list"
        assert len(test_entry["images"]) >= 1, "Entry should have at least 1 image"
        
        # Verify image structure
        image = test_entry["images"][0]
        assert "id" in image, "Image should have id"
        assert "url" in image, "Image should have url"
        assert "filename" in image, "Image should have filename"
        
        print(f"✓ Library list includes images array with {len(test_entry['images'])} image(s)")

    def test_delete_library_image(self, api_client, test_library_entry):
        """Test DELETE /api/projects/:id/library/entries/:entryId/images/:imageId"""
        entry_id = test_library_entry["id"]
        
        # First upload an image
        image_file = create_test_image()
        files = {'file': ('test_delete_image.jpg', image_file, 'image/jpeg')}
        headers = {"Authorization": api_client.headers["Authorization"]}
        
        upload_response = requests.post(
            f"{BASE_URL}/api/projects/{PROJECT_ID}/library/entries/{entry_id}/images",
            files=files,
            headers=headers
        )
        assert upload_response.status_code == 200, f"Upload failed: {upload_response.text}"
        image_id = upload_response.json()["id"]
        
        # Now delete the image
        delete_response = api_client.delete(
            f"{BASE_URL}/api/projects/{PROJECT_ID}/library/entries/{entry_id}/images/{image_id}"
        )
        assert delete_response.status_code == 200, f"Delete failed: {delete_response.text}"
        
        data = delete_response.json()
        assert "message" in data, "Response should contain message"
        
        # Verify image is gone by fetching library
        list_response = api_client.get(f"{BASE_URL}/api/projects/{PROJECT_ID}/library")
        assert list_response.status_code == 200
        
        # Find our test entry and verify image is removed
        for entry in list_response.json()["entries"]:
            if entry["id"] == entry_id:
                image_ids = [img["id"] for img in entry.get("images", [])]
                assert image_id not in image_ids, "Deleted image should not be in entry"
                break
        
        print(f"✓ Image deleted successfully: {image_id}")

    def test_upload_image_to_nonexistent_entry(self, api_client):
        """Test upload to non-existent entry returns 404"""
        fake_entry_id = "00000000-0000-0000-0000-000000000000"
        
        image_file = create_test_image()
        files = {'file': ('test_image.jpg', image_file, 'image/jpeg')}
        headers = {"Authorization": api_client.headers["Authorization"]}
        
        response = requests.post(
            f"{BASE_URL}/api/projects/{PROJECT_ID}/library/entries/{fake_entry_id}/images",
            files=files,
            headers=headers
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Upload to non-existent entry returns 404")

    def test_delete_nonexistent_image(self, api_client, test_library_entry):
        """Test delete non-existent image returns 404"""
        entry_id = test_library_entry["id"]
        fake_image_id = "00000000-0000-0000-0000-000000000000"
        
        response = api_client.delete(
            f"{BASE_URL}/api/projects/{PROJECT_ID}/library/entries/{entry_id}/images/{fake_image_id}"
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Delete non-existent image returns 404")


class TestLibraryEntryWithImages:
    """Test library entry CRUD with images"""

    def test_create_entry_has_empty_images_array(self, api_client):
        """Test newly created entry has empty images array"""
        payload = {
            "title": "TEST_Entry_Empty_Images",
            "description": "Test entry",
            "is_public": False,
            "folder_id": None
        }
        
        response = api_client.post(f"{BASE_URL}/api/projects/{PROJECT_ID}/library/entries", json=payload)
        assert response.status_code == 200, f"Create failed: {response.text}"
        
        data = response.json()
        assert "images" in data, "Entry should have images field"
        assert isinstance(data["images"], list), "images should be a list"
        assert len(data["images"]) == 0, "New entry should have empty images array"
        
        # Cleanup
        api_client.delete(f"{BASE_URL}/api/projects/{PROJECT_ID}/library/entries/{data['id']}")
        print("✓ New entry has empty images array")

    def test_get_single_entry_includes_images(self, api_client, test_library_entry):
        """Test GET single entry includes images"""
        entry_id = test_library_entry["id"]
        
        # Upload an image first
        image_file = create_test_image()
        files = {'file': ('test_single.jpg', image_file, 'image/jpeg')}
        headers = {"Authorization": api_client.headers["Authorization"]}
        
        requests.post(
            f"{BASE_URL}/api/projects/{PROJECT_ID}/library/entries/{entry_id}/images",
            files=files,
            headers=headers
        )
        
        # Get single entry
        response = api_client.get(f"{BASE_URL}/api/projects/{PROJECT_ID}/library/entries/{entry_id}")
        assert response.status_code == 200, f"Get entry failed: {response.text}"
        
        data = response.json()
        assert "images" in data, "Entry should have images field"
        assert len(data["images"]) >= 1, "Entry should have at least 1 image"
        
        print(f"✓ Single entry includes {len(data['images'])} image(s)")
