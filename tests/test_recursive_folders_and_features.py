"""
Test suite for Self-Sufficient Life App - Iteration 7
Testing: Recursive folders, view counts, search in descriptions, config endpoint, folder path APIs
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestConfig:
    """Test app configuration endpoint"""
    
    def test_config_endpoint_returns_app_name(self):
        """GET /api/config returns app_name"""
        response = requests.get(f"{BASE_URL}/api/config")
        assert response.status_code == 200
        data = response.json()
        assert "app_name" in data
        assert isinstance(data["app_name"], str)
        print(f"✓ Config endpoint returns app_name: {data['app_name']}")
    
    def test_config_endpoint_returns_email_configured(self):
        """GET /api/config returns email_configured status"""
        response = requests.get(f"{BASE_URL}/api/config")
        assert response.status_code == 200
        data = response.json()
        assert "email_configured" in data
        assert isinstance(data["email_configured"], bool)
        print(f"✓ Config endpoint returns email_configured: {data['email_configured']}")


class TestAuthentication:
    """Test authentication for subsequent tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@selfsufficient.app",
            "password": "admin123"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        token = response.json().get("access_token")
        assert token, "No access token returned"
        print(f"✓ Authentication successful")
        return token
    
    @pytest.fixture(scope="class")
    def project_id(self, auth_token):
        """Get or create a test project"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # List projects
        response = requests.get(f"{BASE_URL}/api/projects", headers=headers)
        assert response.status_code == 200
        projects = response.json().get("projects", [])
        
        if projects:
            project_id = projects[0]["id"]
            print(f"✓ Using existing project: {project_id}")
            return project_id
        
        # Create a test project
        response = requests.post(f"{BASE_URL}/api/projects", json={
            "name": "TEST_Recursive_Folders_Project",
            "description": "Test project for recursive folder testing",
            "is_public": False
        }, headers=headers)
        assert response.status_code == 200
        project_id = response.json()["id"]
        print(f"✓ Created test project: {project_id}")
        return project_id


class TestGalleryRecursiveFolders(TestAuthentication):
    """Test Gallery recursive folder functionality"""
    
    def test_create_root_folder(self, auth_token, project_id):
        """Create a folder in gallery root"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(
            f"{BASE_URL}/api/projects/{project_id}/gallery/folders",
            json={"name": "TEST_Gallery_Parent", "parent_id": None},
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "TEST_Gallery_Parent"
        assert data["parent_id"] is None
        print(f"✓ Created root gallery folder: {data['id']}")
        return data["id"]
    
    def test_create_subfolder(self, auth_token, project_id):
        """Create a subfolder inside parent folder"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # First create parent folder
        parent_response = requests.post(
            f"{BASE_URL}/api/projects/{project_id}/gallery/folders",
            json={"name": "TEST_Gallery_Parent2", "parent_id": None},
            headers=headers
        )
        assert parent_response.status_code == 200
        parent_id = parent_response.json()["id"]
        
        # Create subfolder
        response = requests.post(
            f"{BASE_URL}/api/projects/{project_id}/gallery/folders",
            json={"name": "TEST_Gallery_Child", "parent_id": parent_id},
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "TEST_Gallery_Child"
        assert data["parent_id"] == parent_id
        print(f"✓ Created gallery subfolder with parent_id: {data['parent_id']}")
        return data["id"], parent_id
    
    def test_gallery_folder_path_endpoint(self, auth_token, project_id):
        """Test GET /api/projects/{id}/gallery/folders/{folderId}/path returns breadcrumb path"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Create parent folder
        parent_response = requests.post(
            f"{BASE_URL}/api/projects/{project_id}/gallery/folders",
            json={"name": "TEST_Gallery_PathParent", "parent_id": None},
            headers=headers
        )
        assert parent_response.status_code == 200
        parent_id = parent_response.json()["id"]
        
        # Create child folder
        child_response = requests.post(
            f"{BASE_URL}/api/projects/{project_id}/gallery/folders",
            json={"name": "TEST_Gallery_PathChild", "parent_id": parent_id},
            headers=headers
        )
        assert child_response.status_code == 200
        child_id = child_response.json()["id"]
        
        # Get folder path
        path_response = requests.get(
            f"{BASE_URL}/api/projects/{project_id}/gallery/folders/{child_id}/path",
            headers=headers
        )
        assert path_response.status_code == 200
        data = path_response.json()
        assert "path" in data
        assert len(data["path"]) == 2  # Parent and Child
        assert data["path"][0]["name"] == "TEST_Gallery_PathParent"
        assert data["path"][1]["name"] == "TEST_Gallery_PathChild"
        print(f"✓ Gallery folder path returns correct breadcrumb: {[p['name'] for p in data['path']]}")
    
    def test_list_gallery_with_folder_filter(self, auth_token, project_id):
        """Test listing gallery contents filtered by folder_id"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Create parent folder
        parent_response = requests.post(
            f"{BASE_URL}/api/projects/{project_id}/gallery/folders",
            json={"name": "TEST_Gallery_ListParent", "parent_id": None},
            headers=headers
        )
        parent_id = parent_response.json()["id"]
        
        # Create subfolder
        child_response = requests.post(
            f"{BASE_URL}/api/projects/{project_id}/gallery/folders",
            json={"name": "TEST_Gallery_ListChild", "parent_id": parent_id},
            headers=headers
        )
        child_id = child_response.json()["id"]
        
        # List contents of parent folder
        response = requests.get(
            f"{BASE_URL}/api/projects/{project_id}/gallery?folder_id={parent_id}",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "folders" in data
        # Child folder should be in the list
        folder_names = [f["name"] for f in data["folders"]]
        assert "TEST_Gallery_ListChild" in folder_names
        print(f"✓ Gallery folder listing shows subfolders correctly")


class TestLibraryRecursiveFolders(TestAuthentication):
    """Test Library recursive folder functionality"""
    
    def test_create_library_root_folder(self, auth_token, project_id):
        """Create a folder in library root"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(
            f"{BASE_URL}/api/projects/{project_id}/library/folders",
            json={"name": "TEST_Library_Parent", "parent_id": None},
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "TEST_Library_Parent"
        assert data["parent_id"] is None
        print(f"✓ Created root library folder: {data['id']}")
        return data["id"]
    
    def test_create_library_subfolder(self, auth_token, project_id):
        """Create a subfolder inside parent library folder"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # First create parent folder
        parent_response = requests.post(
            f"{BASE_URL}/api/projects/{project_id}/library/folders",
            json={"name": "TEST_Library_Parent2", "parent_id": None},
            headers=headers
        )
        assert parent_response.status_code == 200
        parent_id = parent_response.json()["id"]
        
        # Create subfolder
        response = requests.post(
            f"{BASE_URL}/api/projects/{project_id}/library/folders",
            json={"name": "TEST_Library_Child", "parent_id": parent_id},
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "TEST_Library_Child"
        assert data["parent_id"] == parent_id
        print(f"✓ Created library subfolder with parent_id: {data['parent_id']}")
        return data["id"], parent_id
    
    def test_library_folder_path_endpoint(self, auth_token, project_id):
        """Test GET /api/projects/{id}/library/folders/{folderId}/path returns breadcrumb path"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Create parent folder
        parent_response = requests.post(
            f"{BASE_URL}/api/projects/{project_id}/library/folders",
            json={"name": "TEST_Library_PathParent", "parent_id": None},
            headers=headers
        )
        assert parent_response.status_code == 200
        parent_id = parent_response.json()["id"]
        
        # Create child folder
        child_response = requests.post(
            f"{BASE_URL}/api/projects/{project_id}/library/folders",
            json={"name": "TEST_Library_PathChild", "parent_id": parent_id},
            headers=headers
        )
        assert child_response.status_code == 200
        child_id = child_response.json()["id"]
        
        # Get folder path
        path_response = requests.get(
            f"{BASE_URL}/api/projects/{project_id}/library/folders/{child_id}/path",
            headers=headers
        )
        assert path_response.status_code == 200
        data = path_response.json()
        assert "path" in data
        assert len(data["path"]) == 2  # Parent and Child
        assert data["path"][0]["name"] == "TEST_Library_PathParent"
        assert data["path"][1]["name"] == "TEST_Library_PathChild"
        print(f"✓ Library folder path returns correct breadcrumb: {[p['name'] for p in data['path']]}")


class TestViewCounts(TestAuthentication):
    """Test view counts on blog and library entries"""
    
    def test_blog_entry_has_views_field(self, auth_token, project_id):
        """Blog entries should have views field"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Create a blog entry
        response = requests.post(
            f"{BASE_URL}/api/projects/{project_id}/blog",
            json={
                "title": "TEST_Blog_ViewCount",
                "description": "Testing view count feature",
                "is_public": True
            },
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "views" in data
        assert data["views"] == 0  # Initial view count should be 0
        print(f"✓ Blog entry has views field with initial value: {data['views']}")
        return data["id"]
    
    def test_library_entry_has_views_field(self, auth_token, project_id):
        """Library entries should have views field"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Create a library entry
        response = requests.post(
            f"{BASE_URL}/api/projects/{project_id}/library/entries",
            json={
                "title": "TEST_Library_ViewCount",
                "description": "Testing view count feature",
                "is_public": True
            },
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "views" in data
        assert data["views"] == 0  # Initial view count should be 0
        print(f"✓ Library entry has views field with initial value: {data['views']}")
        return data["id"]
    
    def test_blog_list_includes_views(self, auth_token, project_id):
        """Blog list should include views for each entry"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/projects/{project_id}/blog",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        if data["entries"]:
            for entry in data["entries"]:
                assert "views" in entry, f"Entry {entry['id']} missing views field"
            print(f"✓ Blog list includes views field for all {len(data['entries'])} entries")
        else:
            print("✓ Blog list is empty but endpoint works")
    
    def test_library_list_includes_views(self, auth_token, project_id):
        """Library list should include views for each entry"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/projects/{project_id}/library",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        if data["entries"]:
            for entry in data["entries"]:
                assert "views" in entry, f"Entry {entry['id']} missing views field"
            print(f"✓ Library list includes views field for all {len(data['entries'])} entries")
        else:
            print("✓ Library list is empty but endpoint works")


class TestSearchInDescriptions(TestAuthentication):
    """Test search functionality includes description content"""
    
    def test_blog_search_finds_description_content(self, auth_token, project_id):
        """Blog search should find entries by description content"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Create a blog entry with unique description
        unique_term = "UNIQUEBLOGDESC123"
        response = requests.post(
            f"{BASE_URL}/api/projects/{project_id}/blog",
            json={
                "title": "TEST_Blog_Search",
                "description": f"This entry contains {unique_term} in description",
                "is_public": False
            },
            headers=headers
        )
        assert response.status_code == 200
        entry_id = response.json()["id"]
        
        # Search for the unique term
        search_response = requests.get(
            f"{BASE_URL}/api/projects/{project_id}/blog?search={unique_term}",
            headers=headers
        )
        assert search_response.status_code == 200
        data = search_response.json()
        entry_ids = [e["id"] for e in data["entries"]]
        assert entry_id in entry_ids, f"Search did not find entry by description content"
        print(f"✓ Blog search finds entries by description content")
    
    def test_library_search_finds_description_content(self, auth_token, project_id):
        """Library search should find entries by description content"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Create a library entry with unique description
        unique_term = "UNIQUELIBDESC456"
        response = requests.post(
            f"{BASE_URL}/api/projects/{project_id}/library/entries",
            json={
                "title": "TEST_Library_Search",
                "description": f"This entry contains {unique_term} in description",
                "is_public": False
            },
            headers=headers
        )
        assert response.status_code == 200
        entry_id = response.json()["id"]
        
        # Search for the unique term
        search_response = requests.get(
            f"{BASE_URL}/api/projects/{project_id}/library?search={unique_term}",
            headers=headers
        )
        assert search_response.status_code == 200
        data = search_response.json()
        entry_ids = [e["id"] for e in data["entries"]]
        assert entry_id in entry_ids, f"Search did not find entry by description content"
        print(f"✓ Library search finds entries by description content")
    
    def test_diary_search_finds_story_content(self, auth_token, project_id):
        """Diary search should find entries by story content"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Create a diary entry with unique story content
        unique_term = "UNIQUEDIARYSTORY789"
        response = requests.post(
            f"{BASE_URL}/api/projects/{project_id}/diary",
            json={
                "title": "TEST_Diary_Search",
                "story": f"This diary entry contains {unique_term} in the story"
            },
            headers=headers
        )
        assert response.status_code == 200
        entry_id = response.json()["id"]
        
        # Search for the unique term
        search_response = requests.get(
            f"{BASE_URL}/api/projects/{project_id}/diary?search={unique_term}",
            headers=headers
        )
        assert search_response.status_code == 200
        data = search_response.json()
        entry_ids = [e["id"] for e in data["entries"]]
        assert entry_id in entry_ids, f"Search did not find entry by story content"
        print(f"✓ Diary search finds entries by story content")


class TestCleanup(TestAuthentication):
    """Cleanup test data"""
    
    def test_cleanup_test_data(self, auth_token, project_id):
        """Clean up TEST_ prefixed data"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Clean up gallery folders
        gallery_response = requests.get(
            f"{BASE_URL}/api/projects/{project_id}/gallery",
            headers=headers
        )
        if gallery_response.status_code == 200:
            folders = gallery_response.json().get("folders", [])
            for folder in folders:
                if folder["name"].startswith("TEST_"):
                    requests.delete(
                        f"{BASE_URL}/api/projects/{project_id}/gallery/folders/{folder['id']}",
                        headers=headers
                    )
        
        # Clean up library folders
        library_response = requests.get(
            f"{BASE_URL}/api/projects/{project_id}/library",
            headers=headers
        )
        if library_response.status_code == 200:
            folders = library_response.json().get("folders", [])
            for folder in folders:
                if folder["name"].startswith("TEST_"):
                    requests.delete(
                        f"{BASE_URL}/api/projects/{project_id}/library/folders/{folder['id']}",
                        headers=headers
                    )
            entries = library_response.json().get("entries", [])
            for entry in entries:
                if entry["title"].startswith("TEST_"):
                    requests.delete(
                        f"{BASE_URL}/api/projects/{project_id}/library/entries/{entry['id']}",
                        headers=headers
                    )
        
        # Clean up blog entries
        blog_response = requests.get(
            f"{BASE_URL}/api/projects/{project_id}/blog",
            headers=headers
        )
        if blog_response.status_code == 200:
            entries = blog_response.json().get("entries", [])
            for entry in entries:
                if entry["title"].startswith("TEST_"):
                    requests.delete(
                        f"{BASE_URL}/api/projects/{project_id}/blog/{entry['id']}",
                        headers=headers
                    )
        
        # Clean up diary entries
        diary_response = requests.get(
            f"{BASE_URL}/api/projects/{project_id}/diary",
            headers=headers
        )
        if diary_response.status_code == 200:
            entries = diary_response.json().get("entries", [])
            for entry in entries:
                if entry["title"].startswith("TEST_"):
                    requests.delete(
                        f"{BASE_URL}/api/projects/{project_id}/diary/{entry['id']}",
                        headers=headers
                    )
        
        print("✓ Cleanup completed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
