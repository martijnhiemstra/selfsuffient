"""
Test suite for Daily Reminders feature and Start/End of Day renaming
Tests:
- GET /api/auth/me returns daily_reminders field
- PUT /api/auth/settings updates daily_reminders
- POST /api/cron/send-daily-reminders endpoint
- Public project page view counts
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "admin@selfsufficient.app"
TEST_PASSWORD = "admin123"


class TestDailyRemindersFeature:
    """Tests for daily reminders feature"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        self.token = data["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.user_id = data["user"]["id"]
    
    def test_auth_me_returns_daily_reminders_field(self):
        """GET /api/auth/me should return daily_reminders field"""
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=self.headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "daily_reminders" in data, "daily_reminders field missing from /api/auth/me response"
        assert isinstance(data["daily_reminders"], bool), "daily_reminders should be a boolean"
        print(f"✓ GET /api/auth/me returns daily_reminders: {data['daily_reminders']}")
    
    def test_update_settings_daily_reminders_enable(self):
        """PUT /api/auth/settings should enable daily_reminders"""
        response = requests.put(
            f"{BASE_URL}/api/auth/settings",
            headers=self.headers,
            json={"daily_reminders": True}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["daily_reminders"] == True, "daily_reminders should be True after enabling"
        print("✓ PUT /api/auth/settings enables daily_reminders")
    
    def test_update_settings_daily_reminders_disable(self):
        """PUT /api/auth/settings should disable daily_reminders"""
        response = requests.put(
            f"{BASE_URL}/api/auth/settings",
            headers=self.headers,
            json={"daily_reminders": False}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["daily_reminders"] == False, "daily_reminders should be False after disabling"
        print("✓ PUT /api/auth/settings disables daily_reminders")
    
    def test_settings_update_persists(self):
        """Verify settings update persists in database"""
        # Enable daily reminders
        requests.put(
            f"{BASE_URL}/api/auth/settings",
            headers=self.headers,
            json={"daily_reminders": True}
        )
        
        # Verify via GET /api/auth/me
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=self.headers)
        assert response.status_code == 200
        assert response.json()["daily_reminders"] == True
        
        # Disable daily reminders
        requests.put(
            f"{BASE_URL}/api/auth/settings",
            headers=self.headers,
            json={"daily_reminders": False}
        )
        
        # Verify via GET /api/auth/me
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=self.headers)
        assert response.status_code == 200
        assert response.json()["daily_reminders"] == False
        print("✓ Settings update persists correctly")


class TestCronDailyReminders:
    """Tests for daily reminders cron endpoint"""
    
    def test_cron_endpoint_exists(self):
        """POST /api/cron/send-daily-reminders should exist and return response"""
        response = requests.post(f"{BASE_URL}/api/cron/send-daily-reminders")
        assert response.status_code == 200, f"Cron endpoint failed: {response.text}"
        
        data = response.json()
        assert "message" in data, "Response should have message field"
        assert "sent" in data, "Response should have sent field"
        # total_users is only present when there are users with reminders enabled
        print(f"✓ POST /api/cron/send-daily-reminders returns: {data}")
    
    def test_cron_processes_users_with_reminders_enabled(self):
        """Cron should process users with daily_reminders enabled"""
        # First login and enable daily reminders
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Enable daily reminders
        requests.put(
            f"{BASE_URL}/api/auth/settings",
            headers=headers,
            json={"daily_reminders": True}
        )
        
        # Call cron endpoint
        response = requests.post(f"{BASE_URL}/api/cron/send-daily-reminders")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_users"] >= 1, "Should have at least 1 user with reminders enabled"
        print(f"✓ Cron processed {data['total_users']} users with reminders enabled")
        
        # Cleanup - disable daily reminders
        requests.put(
            f"{BASE_URL}/api/auth/settings",
            headers=headers,
            json={"daily_reminders": False}
        )


class TestPublicProjectViewCounts:
    """Tests for public project page view counts"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - get auth token and create test project"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        self.token = data["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_blog_entry_has_views_field(self):
        """Blog entries should have views field"""
        # Create a test project
        project_response = requests.post(
            f"{BASE_URL}/api/projects",
            headers=self.headers,
            json={"name": "TEST_ViewCount_Project", "description": "Test project", "is_public": True}
        )
        assert project_response.status_code == 200
        project_id = project_response.json()["id"]
        
        try:
            # Create a blog entry
            blog_response = requests.post(
                f"{BASE_URL}/api/projects/{project_id}/blog",
                headers=self.headers,
                json={"title": "TEST_Blog_Entry", "description": "Test content", "is_public": True}
            )
            assert blog_response.status_code == 200
            blog_data = blog_response.json()
            
            assert "views" in blog_data, "Blog entry should have views field"
            assert blog_data["views"] == 0, "New blog entry should have 0 views"
            print(f"✓ Blog entry has views field with initial value: {blog_data['views']}")
            
        finally:
            # Cleanup
            requests.delete(f"{BASE_URL}/api/projects/{project_id}", headers=self.headers)
    
    def test_library_entry_has_views_field(self):
        """Library entries should have views field"""
        # Create a test project
        project_response = requests.post(
            f"{BASE_URL}/api/projects",
            headers=self.headers,
            json={"name": "TEST_ViewCount_Library_Project", "description": "Test project", "is_public": True}
        )
        assert project_response.status_code == 200
        project_id = project_response.json()["id"]
        
        try:
            # Create a library entry
            library_response = requests.post(
                f"{BASE_URL}/api/projects/{project_id}/library/entries",
                headers=self.headers,
                json={"title": "TEST_Library_Entry", "description": "Test content", "is_public": True}
            )
            assert library_response.status_code == 200
            library_data = library_response.json()
            
            assert "views" in library_data, "Library entry should have views field"
            assert library_data["views"] == 0, "New library entry should have 0 views"
            print(f"✓ Library entry has views field with initial value: {library_data['views']}")
            
        finally:
            # Cleanup
            requests.delete(f"{BASE_URL}/api/projects/{project_id}", headers=self.headers)
    
    def test_public_blog_entry_shows_zero_views(self):
        """Public blog entry should show 0 views initially"""
        # Create a test project
        project_response = requests.post(
            f"{BASE_URL}/api/projects",
            headers=self.headers,
            json={"name": "TEST_Public_Blog_Project", "description": "Test project", "is_public": True}
        )
        assert project_response.status_code == 200
        project_id = project_response.json()["id"]
        
        try:
            # Create a public blog entry
            blog_response = requests.post(
                f"{BASE_URL}/api/projects/{project_id}/blog",
                headers=self.headers,
                json={"title": "TEST_Public_Blog", "description": "Test content", "is_public": True}
            )
            assert blog_response.status_code == 200
            entry_id = blog_response.json()["id"]
            
            # Get public blog list
            public_response = requests.get(f"{BASE_URL}/api/public/projects/{project_id}/blog")
            assert public_response.status_code == 200
            
            entries = public_response.json()["entries"]
            test_entry = next((e for e in entries if e["id"] == entry_id), None)
            assert test_entry is not None, "Test entry should be in public list"
            assert test_entry["views"] == 0, "Public blog entry should show 0 views initially"
            print(f"✓ Public blog entry shows {test_entry['views']} views")
            
        finally:
            # Cleanup
            requests.delete(f"{BASE_URL}/api/projects/{project_id}", headers=self.headers)


class TestLoginResponseIncludesDailyReminders:
    """Test that login response includes daily_reminders field"""
    
    def test_login_response_has_daily_reminders(self):
        """Login response should include daily_reminders in user object"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        
        data = response.json()
        assert "user" in data, "Login response should have user object"
        assert "daily_reminders" in data["user"], "User object should have daily_reminders field"
        assert isinstance(data["user"]["daily_reminders"], bool), "daily_reminders should be boolean"
        print(f"✓ Login response includes daily_reminders: {data['user']['daily_reminders']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
