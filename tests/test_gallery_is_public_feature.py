"""
Test Gallery is_public feature and Public Project Page Gallery/Search/Sort
Tests:
1. Gallery folder creation with is_public field
2. Gallery folder update with is_public field
3. GET /api/public/projects/{id}/gallery returns only public folders
4. Public project page Gallery tab functionality
5. Public project page Blog/Library tabs have search and sort
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestGalleryIsPublicFeature:
    """Test gallery folder is_public field functionality"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test data - login and get project"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@selfsufficient.app",
            "password": "admin123"
        })
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        
        token = login_response.json()["access_token"]
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        # Get or create a public project
        projects_response = self.session.get(f"{BASE_URL}/api/projects")
        assert projects_response.status_code == 200
        
        projects = projects_response.json()["projects"]
        public_project = next((p for p in projects if p.get("is_public")), None)
        
        if public_project:
            self.project_id = public_project["id"]
        else:
            # Create a public project for testing
            create_response = self.session.post(f"{BASE_URL}/api/projects", json={
                "name": "TEST_Public_Project_Gallery",
                "description": "Test project for gallery is_public feature",
                "is_public": True
            })
            assert create_response.status_code == 200
            self.project_id = create_response.json()["id"]
        
        yield
        
        # Cleanup - delete test folders
        # Get all folders and delete TEST_ prefixed ones
        gallery_response = self.session.get(f"{BASE_URL}/api/projects/{self.project_id}/gallery")
        if gallery_response.status_code == 200:
            folders = gallery_response.json().get("folders", [])
            for folder in folders:
                if folder["name"].startswith("TEST_"):
                    self.session.delete(f"{BASE_URL}/api/projects/{self.project_id}/gallery/folders/{folder['id']}")
    
    def test_create_gallery_folder_with_is_public_false(self):
        """Test creating a gallery folder with is_public=false (default)"""
        folder_name = f"TEST_Private_Folder_{uuid.uuid4().hex[:8]}"
        
        response = self.session.post(
            f"{BASE_URL}/api/projects/{self.project_id}/gallery/folders",
            json={"name": folder_name, "is_public": False}
        )
        
        assert response.status_code == 200, f"Failed to create folder: {response.text}"
        data = response.json()
        
        # Verify is_public field exists and is False
        assert "is_public" in data, "is_public field missing in response"
        assert data["is_public"] == False, f"Expected is_public=False, got {data['is_public']}"
        assert data["name"] == folder_name
        
        print(f"✓ Created private folder: {folder_name}, is_public={data['is_public']}")
    
    def test_create_gallery_folder_with_is_public_true(self):
        """Test creating a gallery folder with is_public=true"""
        folder_name = f"TEST_Public_Folder_{uuid.uuid4().hex[:8]}"
        
        response = self.session.post(
            f"{BASE_URL}/api/projects/{self.project_id}/gallery/folders",
            json={"name": folder_name, "is_public": True}
        )
        
        assert response.status_code == 200, f"Failed to create folder: {response.text}"
        data = response.json()
        
        # Verify is_public field exists and is True
        assert "is_public" in data, "is_public field missing in response"
        assert data["is_public"] == True, f"Expected is_public=True, got {data['is_public']}"
        assert data["name"] == folder_name
        
        print(f"✓ Created public folder: {folder_name}, is_public={data['is_public']}")
    
    def test_update_gallery_folder_is_public(self):
        """Test updating a gallery folder's is_public field"""
        # Create a private folder first
        folder_name = f"TEST_Update_Folder_{uuid.uuid4().hex[:8]}"
        
        create_response = self.session.post(
            f"{BASE_URL}/api/projects/{self.project_id}/gallery/folders",
            json={"name": folder_name, "is_public": False}
        )
        assert create_response.status_code == 200
        folder_id = create_response.json()["id"]
        
        # Update to public
        update_response = self.session.put(
            f"{BASE_URL}/api/projects/{self.project_id}/gallery/folders/{folder_id}",
            json={"is_public": True}
        )
        
        assert update_response.status_code == 200, f"Failed to update folder: {update_response.text}"
        data = update_response.json()
        
        assert data["is_public"] == True, f"Expected is_public=True after update, got {data['is_public']}"
        
        print(f"✓ Updated folder to public: {folder_name}, is_public={data['is_public']}")
    
    def test_gallery_list_returns_is_public_field(self):
        """Test that gallery list endpoint returns is_public field for folders"""
        # Create a test folder
        folder_name = f"TEST_List_Folder_{uuid.uuid4().hex[:8]}"
        
        self.session.post(
            f"{BASE_URL}/api/projects/{self.project_id}/gallery/folders",
            json={"name": folder_name, "is_public": True}
        )
        
        # Get gallery list
        response = self.session.get(f"{BASE_URL}/api/projects/{self.project_id}/gallery")
        
        assert response.status_code == 200, f"Failed to get gallery: {response.text}"
        data = response.json()
        
        assert "folders" in data, "folders field missing in response"
        
        # Find our test folder
        test_folder = next((f for f in data["folders"] if f["name"] == folder_name), None)
        assert test_folder is not None, f"Test folder {folder_name} not found in list"
        assert "is_public" in test_folder, "is_public field missing in folder list item"
        
        print(f"✓ Gallery list returns is_public field for folders")


class TestPublicGalleryEndpoint:
    """Test public gallery endpoint returns only public folders"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test data"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@selfsufficient.app",
            "password": "admin123"
        })
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        # Get or create a public project
        projects_response = self.session.get(f"{BASE_URL}/api/projects")
        projects = projects_response.json()["projects"]
        public_project = next((p for p in projects if p.get("is_public")), None)
        
        if public_project:
            self.project_id = public_project["id"]
        else:
            create_response = self.session.post(f"{BASE_URL}/api/projects", json={
                "name": "TEST_Public_Project_Gallery_2",
                "description": "Test project for public gallery",
                "is_public": True
            })
            self.project_id = create_response.json()["id"]
        
        # Create test folders - one public, one private
        self.public_folder_name = f"TEST_Public_{uuid.uuid4().hex[:8]}"
        self.private_folder_name = f"TEST_Private_{uuid.uuid4().hex[:8]}"
        
        # Create public folder
        pub_response = self.session.post(
            f"{BASE_URL}/api/projects/{self.project_id}/gallery/folders",
            json={"name": self.public_folder_name, "is_public": True}
        )
        self.public_folder_id = pub_response.json()["id"] if pub_response.status_code == 200 else None
        
        # Create private folder
        priv_response = self.session.post(
            f"{BASE_URL}/api/projects/{self.project_id}/gallery/folders",
            json={"name": self.private_folder_name, "is_public": False}
        )
        self.private_folder_id = priv_response.json()["id"] if priv_response.status_code == 200 else None
        
        yield
        
        # Cleanup
        if self.public_folder_id:
            self.session.delete(f"{BASE_URL}/api/projects/{self.project_id}/gallery/folders/{self.public_folder_id}")
        if self.private_folder_id:
            self.session.delete(f"{BASE_URL}/api/projects/{self.project_id}/gallery/folders/{self.private_folder_id}")
    
    def test_public_gallery_endpoint_exists(self):
        """Test that public gallery endpoint exists and returns 200"""
        # Use a new session without auth
        public_session = requests.Session()
        
        response = public_session.get(f"{BASE_URL}/api/public/projects/{self.project_id}/gallery")
        
        assert response.status_code == 200, f"Public gallery endpoint failed: {response.text}"
        data = response.json()
        
        assert "folders" in data, "folders field missing in public gallery response"
        assert "images" in data, "images field missing in public gallery response"
        
        print(f"✓ Public gallery endpoint exists and returns 200")
    
    def test_public_gallery_returns_only_public_folders(self):
        """Test that public gallery endpoint returns only public folders"""
        # Use a new session without auth
        public_session = requests.Session()
        
        response = public_session.get(f"{BASE_URL}/api/public/projects/{self.project_id}/gallery")
        
        assert response.status_code == 200
        data = response.json()
        
        folder_names = [f["name"] for f in data["folders"]]
        
        # Public folder should be in the list
        assert self.public_folder_name in folder_names, f"Public folder {self.public_folder_name} not found in public gallery"
        
        # Private folder should NOT be in the list
        assert self.private_folder_name not in folder_names, f"Private folder {self.private_folder_name} should not be in public gallery"
        
        print(f"✓ Public gallery returns only public folders")
        print(f"  - Public folder '{self.public_folder_name}' is visible")
        print(f"  - Private folder '{self.private_folder_name}' is hidden")
    
    def test_public_gallery_supports_search(self):
        """Test that public gallery endpoint supports search parameter"""
        public_session = requests.Session()
        
        # Search for the public folder
        response = public_session.get(
            f"{BASE_URL}/api/public/projects/{self.project_id}/gallery",
            params={"search": self.public_folder_name[:10]}
        )
        
        assert response.status_code == 200, f"Public gallery search failed: {response.text}"
        
        print(f"✓ Public gallery supports search parameter")
    
    def test_public_gallery_supports_sort(self):
        """Test that public gallery endpoint supports sort parameters"""
        public_session = requests.Session()
        
        # Test sort by name ascending
        response = public_session.get(
            f"{BASE_URL}/api/public/projects/{self.project_id}/gallery",
            params={"sort_by": "name", "sort_order": "asc"}
        )
        
        assert response.status_code == 200, f"Public gallery sort failed: {response.text}"
        
        # Test sort by created_at descending
        response2 = public_session.get(
            f"{BASE_URL}/api/public/projects/{self.project_id}/gallery",
            params={"sort_by": "created_at", "sort_order": "desc"}
        )
        
        assert response2.status_code == 200
        
        print(f"✓ Public gallery supports sort parameters")


class TestPublicBlogLibrarySearchSort:
    """Test public blog and library endpoints support search and sort"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test data"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@selfsufficient.app",
            "password": "admin123"
        })
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        # Get or create a public project
        projects_response = self.session.get(f"{BASE_URL}/api/projects")
        projects = projects_response.json()["projects"]
        public_project = next((p for p in projects if p.get("is_public")), None)
        
        if public_project:
            self.project_id = public_project["id"]
        else:
            create_response = self.session.post(f"{BASE_URL}/api/projects", json={
                "name": "TEST_Public_Project_Search",
                "description": "Test project for search/sort",
                "is_public": True
            })
            self.project_id = create_response.json()["id"]
        
        yield
    
    def test_public_blog_supports_search(self):
        """Test that public blog endpoint supports search parameter"""
        public_session = requests.Session()
        
        response = public_session.get(
            f"{BASE_URL}/api/public/projects/{self.project_id}/blog",
            params={"search": "test"}
        )
        
        assert response.status_code == 200, f"Public blog search failed: {response.text}"
        data = response.json()
        assert "entries" in data, "entries field missing in response"
        
        print(f"✓ Public blog supports search parameter")
    
    def test_public_blog_supports_sort(self):
        """Test that public blog endpoint supports sort parameters"""
        public_session = requests.Session()
        
        # Test sort by title ascending
        response = public_session.get(
            f"{BASE_URL}/api/public/projects/{self.project_id}/blog",
            params={"sort_by": "title", "sort_order": "asc"}
        )
        
        assert response.status_code == 200, f"Public blog sort failed: {response.text}"
        
        # Test sort by created_at descending
        response2 = public_session.get(
            f"{BASE_URL}/api/public/projects/{self.project_id}/blog",
            params={"sort_by": "created_at", "sort_order": "desc"}
        )
        
        assert response2.status_code == 200
        
        print(f"✓ Public blog supports sort parameters")
    
    def test_public_library_supports_search(self):
        """Test that public library endpoint supports search parameter"""
        public_session = requests.Session()
        
        response = public_session.get(
            f"{BASE_URL}/api/public/projects/{self.project_id}/library",
            params={"search": "test"}
        )
        
        assert response.status_code == 200, f"Public library search failed: {response.text}"
        data = response.json()
        assert "entries" in data, "entries field missing in response"
        
        print(f"✓ Public library supports search parameter")
    
    def test_public_library_supports_sort(self):
        """Test that public library endpoint supports sort parameters"""
        public_session = requests.Session()
        
        # Test sort by title ascending
        response = public_session.get(
            f"{BASE_URL}/api/public/projects/{self.project_id}/library",
            params={"sort_by": "title", "sort_order": "asc"}
        )
        
        assert response.status_code == 200, f"Public library sort failed: {response.text}"
        
        # Test sort by created_at descending
        response2 = public_session.get(
            f"{BASE_URL}/api/public/projects/{self.project_id}/library",
            params={"sort_by": "created_at", "sort_order": "desc"}
        )
        
        assert response2.status_code == 200
        
        print(f"✓ Public library supports sort parameters")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
