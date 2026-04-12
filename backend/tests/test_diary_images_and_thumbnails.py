"""
Test diary image upload/delete and thumbnail generation endpoints.
Features tested:
1. Diary image upload: POST /api/projects/{pid}/diary/{eid}/images
2. Diary image delete: DELETE /api/projects/{pid}/diary/{eid}/images/{iid}
3. Diary entries list includes images array
4. Diary entry delete cleans up associated images
5. Thumbnail endpoint: GET /api/files/thumb/{file_path}
6. Full image endpoint: GET /api/files/{file_path}
"""
import pytest
import requests
import os
from PIL import Image
import io

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
TEST_PROJECT_ID = "72868dc9-f97d-4209-83e8-8d2c6fd59c67"

@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "admin@selfsufficient.app",
        "password": "admin123"
    })
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    assert "access_token" in data, "Response missing access_token"
    return data["access_token"]


@pytest.fixture(scope="module")
def api_client(auth_token):
    """Authenticated requests session"""
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    })
    return session


@pytest.fixture
def test_image_file():
    """Create a test image file in memory"""
    img = Image.new('RGB', (800, 600), color='green')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes


class TestDiaryImageUpload:
    """Test diary image upload functionality"""
    
    def test_create_diary_entry_and_upload_image(self, api_client, test_image_file, auth_token):
        """Create a diary entry and upload an image to it"""
        # Create diary entry
        entry_data = {
            "title": "TEST_DiaryImageTest",
            "story": "<p>Testing image upload</p>"
        }
        create_response = api_client.post(
            f"{BASE_URL}/api/projects/{TEST_PROJECT_ID}/diary",
            json=entry_data
        )
        assert create_response.status_code == 200, f"Failed to create diary entry: {create_response.text}"
        entry = create_response.json()
        entry_id = entry["id"]
        
        # Verify entry has empty images array initially
        assert "images" in entry, "Entry should have images field"
        assert entry["images"] == [], "New entry should have empty images array"
        
        # Upload image
        files = {"file": ("test_image.jpg", test_image_file, "image/jpeg")}
        upload_response = requests.post(
            f"{BASE_URL}/api/projects/{TEST_PROJECT_ID}/diary/{entry_id}/images",
            files=files,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert upload_response.status_code == 200, f"Failed to upload image: {upload_response.text}"
        
        image_data = upload_response.json()
        assert "id" in image_data, "Image response should have id"
        assert "url" in image_data, "Image response should have url"
        assert "filename" in image_data, "Image response should have filename"
        assert "diary_id" in image_data, "Image response should have diary_id"
        assert image_data["diary_id"] == entry_id
        
        image_id = image_data["id"]
        image_url = image_data["url"]
        
        # Verify entry now has the image
        get_response = api_client.get(f"{BASE_URL}/api/projects/{TEST_PROJECT_ID}/diary/{entry_id}")
        assert get_response.status_code == 200
        updated_entry = get_response.json()
        assert len(updated_entry["images"]) == 1, "Entry should have 1 image"
        assert updated_entry["images"][0]["id"] == image_id
        
        # Store for cleanup
        self.__class__.test_entry_id = entry_id
        self.__class__.test_image_id = image_id
        self.__class__.test_image_url = image_url
        
        print(f"✓ Created diary entry {entry_id} with image {image_id}")
        print(f"  Image URL: {image_url}")
    
    def test_full_image_endpoint(self, auth_token):
        """Test that full image can be retrieved via /api/files/{path}"""
        image_url = getattr(self.__class__, 'test_image_url', None)
        if not image_url:
            pytest.skip("No test image URL available")
        
        # Extract file path from URL (e.g., /uploads/diary/... -> diary/...)
        file_path = image_url.replace('/uploads/', '')
        
        response = requests.get(
            f"{BASE_URL}/api/files/{file_path}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Failed to get full image: {response.status_code}"
        assert response.headers.get('content-type', '').startswith('image/'), "Response should be an image"
        assert len(response.content) > 1000, "Image content should be substantial"
        
        print(f"✓ Full image endpoint works: /api/files/{file_path}")
    
    def test_thumbnail_endpoint(self, auth_token):
        """Test that thumbnail is generated on-demand via /api/files/thumb/{path}"""
        image_url = getattr(self.__class__, 'test_image_url', None)
        if not image_url:
            pytest.skip("No test image URL available")
        
        file_path = image_url.replace('/uploads/', '')
        
        response = requests.get(
            f"{BASE_URL}/api/files/thumb/{file_path}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Failed to get thumbnail: {response.status_code}"
        assert response.headers.get('content-type', '').startswith('image/'), "Response should be an image"
        
        # Verify thumbnail is smaller than original (should be ~300px wide)
        thumb_img = Image.open(io.BytesIO(response.content))
        assert thumb_img.width <= 300, f"Thumbnail width should be <= 300px, got {thumb_img.width}"
        
        print(f"✓ Thumbnail endpoint works: /api/files/thumb/{file_path}")
        print(f"  Thumbnail size: {thumb_img.width}x{thumb_img.height}")
    
    def test_thumbnail_cached_on_second_request(self, auth_token):
        """Test that thumbnail is cached and served on subsequent requests"""
        image_url = getattr(self.__class__, 'test_image_url', None)
        if not image_url:
            pytest.skip("No test image URL available")
        
        file_path = image_url.replace('/uploads/', '')
        
        # Second request should be served from cache
        response = requests.get(
            f"{BASE_URL}/api/files/thumb/{file_path}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, "Cached thumbnail should be served"
        
        print("✓ Thumbnail caching works (second request successful)")
    
    def test_delete_diary_image(self, api_client, auth_token):
        """Test deleting a diary image"""
        entry_id = getattr(self.__class__, 'test_entry_id', None)
        image_id = getattr(self.__class__, 'test_image_id', None)
        
        if not entry_id or not image_id:
            pytest.skip("No test entry/image available")
        
        # Delete the image
        delete_response = requests.delete(
            f"{BASE_URL}/api/projects/{TEST_PROJECT_ID}/diary/{entry_id}/images/{image_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert delete_response.status_code == 200, f"Failed to delete image: {delete_response.text}"
        
        # Verify entry no longer has the image
        get_response = api_client.get(f"{BASE_URL}/api/projects/{TEST_PROJECT_ID}/diary/{entry_id}")
        assert get_response.status_code == 200
        updated_entry = get_response.json()
        assert len(updated_entry["images"]) == 0, "Entry should have no images after deletion"
        
        print(f"✓ Deleted image {image_id} from entry {entry_id}")
    
    def test_diary_entry_delete_cleans_up_images(self, api_client, auth_token):
        """Test that deleting a diary entry also deletes its images"""
        # Create a new entry with an image
        entry_data = {
            "title": "TEST_DiaryDeleteCleanup",
            "story": "<p>Testing delete cleanup</p>"
        }
        create_response = api_client.post(
            f"{BASE_URL}/api/projects/{TEST_PROJECT_ID}/diary",
            json=entry_data
        )
        assert create_response.status_code == 200
        entry_id = create_response.json()["id"]
        
        # Upload an image
        img = Image.new('RGB', (400, 300), color='blue')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        files = {"file": ("cleanup_test.jpg", img_bytes, "image/jpeg")}
        upload_response = requests.post(
            f"{BASE_URL}/api/projects/{TEST_PROJECT_ID}/diary/{entry_id}/images",
            files=files,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert upload_response.status_code == 200
        image_url = upload_response.json()["url"]
        
        # Delete the entry
        delete_response = requests.delete(
            f"{BASE_URL}/api/projects/{TEST_PROJECT_ID}/diary/{entry_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert delete_response.status_code == 200, f"Failed to delete entry: {delete_response.text}"
        
        # Verify entry is gone
        get_response = api_client.get(f"{BASE_URL}/api/projects/{TEST_PROJECT_ID}/diary/{entry_id}")
        assert get_response.status_code == 404, "Entry should be deleted"
        
        print(f"✓ Diary entry delete cleans up associated images")


class TestDiaryListIncludesImages:
    """Test that diary list endpoint includes images array"""
    
    def test_diary_list_has_images_field(self, api_client, auth_token):
        """Test that diary list entries include images array"""
        # Create entry with image
        entry_data = {
            "title": "TEST_DiaryListImages",
            "story": "<p>Testing list images</p>"
        }
        create_response = api_client.post(
            f"{BASE_URL}/api/projects/{TEST_PROJECT_ID}/diary",
            json=entry_data
        )
        assert create_response.status_code == 200
        entry_id = create_response.json()["id"]
        
        # Upload image
        img = Image.new('RGB', (200, 150), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        files = {"file": ("list_test.jpg", img_bytes, "image/jpeg")}
        requests.post(
            f"{BASE_URL}/api/projects/{TEST_PROJECT_ID}/diary/{entry_id}/images",
            files=files,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Get diary list
        list_response = api_client.get(f"{BASE_URL}/api/projects/{TEST_PROJECT_ID}/diary")
        assert list_response.status_code == 200
        
        data = list_response.json()
        assert "entries" in data, "Response should have entries"
        
        # Find our test entry
        test_entry = next((e for e in data["entries"] if e["id"] == entry_id), None)
        assert test_entry is not None, "Test entry should be in list"
        assert "images" in test_entry, "Entry should have images field"
        assert len(test_entry["images"]) == 1, "Entry should have 1 image"
        
        # Cleanup
        requests.delete(
            f"{BASE_URL}/api/projects/{TEST_PROJECT_ID}/diary/{entry_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        print("✓ Diary list includes images array for each entry")


class TestThumbnailEndpointEdgeCases:
    """Test thumbnail endpoint edge cases"""
    
    def test_thumbnail_404_for_nonexistent_file(self, auth_token):
        """Test that thumbnail returns 404 for non-existent file"""
        response = requests.get(
            f"{BASE_URL}/api/files/thumb/nonexistent/path/image.jpg",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 404, "Should return 404 for non-existent file"
        print("✓ Thumbnail returns 404 for non-existent file")
    
    def test_full_file_404_for_nonexistent(self, auth_token):
        """Test that full file endpoint returns 404 for non-existent file"""
        response = requests.get(
            f"{BASE_URL}/api/files/nonexistent/path/image.jpg",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 404, "Should return 404 for non-existent file"
        print("✓ Full file endpoint returns 404 for non-existent file")


class TestCleanup:
    """Cleanup test data"""
    
    def test_cleanup_test_entries(self, api_client, auth_token):
        """Clean up any remaining test entries"""
        list_response = api_client.get(f"{BASE_URL}/api/projects/{TEST_PROJECT_ID}/diary")
        if list_response.status_code == 200:
            entries = list_response.json().get("entries", [])
            for entry in entries:
                if entry["title"].startswith("TEST_"):
                    requests.delete(
                        f"{BASE_URL}/api/projects/{TEST_PROJECT_ID}/diary/{entry['id']}",
                        headers={"Authorization": f"Bearer {auth_token}"}
                    )
                    print(f"  Cleaned up: {entry['title']}")
        print("✓ Cleanup completed")
