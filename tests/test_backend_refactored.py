"""
Comprehensive Backend API Tests after Refactoring
Tests all CRUD endpoints for: Auth, Projects, Diary, Blog, Tasks, Routines, Dashboard, Public
"""
import pytest
import requests
import os
from datetime import datetime, timezone

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@selfsufficient.app"
ADMIN_PASSWORD = "admin123"


class TestHealthCheck:
    """Health check endpoint tests - run first"""
    
    def test_health_endpoint(self):
        """Test health check returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "app" in data


class TestAuthentication:
    """Authentication endpoint tests"""
    
    def test_login_success(self):
        """Test successful login with admin credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == ADMIN_EMAIL
        assert data["user"]["is_admin"] == True
    
    def test_login_invalid_credentials(self):
        """Test login with wrong password"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": "wrongpassword"
        })
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self):
        """Test login with non-existent email"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "nonexistent@test.com",
            "password": "anypassword"
        })
        assert response.status_code == 401
    
    def test_get_me_authenticated(self, auth_token):
        """Test getting current user info"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == ADMIN_EMAIL
        assert "id" in data
        assert "name" in data
    
    def test_get_me_unauthenticated(self):
        """Test getting current user without token"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code in [401, 403]


class TestProjectsCRUD:
    """Project CRUD tests"""
    
    def test_create_project(self, auth_token):
        """Test creating a new project"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(f"{BASE_URL}/api/projects", headers=headers, json={
            "name": "TEST_Project_Refactor",
            "description": "Test project for refactoring verification",
            "is_public": False
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "TEST_Project_Refactor"
        assert "id" in data
        assert "created_at" in data
        return data["id"]
    
    def test_list_projects(self, auth_token):
        """Test listing user's projects"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/projects", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "projects" in data
        assert "total" in data
        assert isinstance(data["projects"], list)
    
    def test_get_project(self, auth_token, test_project_id):
        """Test getting a specific project"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/projects/{test_project_id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_project_id
    
    def test_update_project(self, auth_token, test_project_id):
        """Test updating a project"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.put(f"{BASE_URL}/api/projects/{test_project_id}", headers=headers, json={
            "name": "TEST_Project_Updated",
            "description": "Updated description"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "TEST_Project_Updated"
        
        # Verify persistence
        get_response = requests.get(f"{BASE_URL}/api/projects/{test_project_id}", headers=headers)
        assert get_response.json()["name"] == "TEST_Project_Updated"


class TestDiaryCRUD:
    """Diary entries CRUD tests"""
    
    def test_create_diary_entry(self, auth_token, test_project_id):
        """Test creating a diary entry"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(f"{BASE_URL}/api/projects/{test_project_id}/diary", headers=headers, json={
            "title": "TEST_Diary_Entry",
            "story": "This is a test diary entry"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "TEST_Diary_Entry"
        assert "id" in data
        return data["id"]
    
    def test_list_diary_entries(self, auth_token, test_project_id):
        """Test listing diary entries"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/projects/{test_project_id}/diary", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "entries" in data
        assert "total" in data
    
    def test_update_diary_entry(self, auth_token, test_project_id, test_diary_id):
        """Test updating a diary entry"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.put(f"{BASE_URL}/api/projects/{test_project_id}/diary/{test_diary_id}", headers=headers, json={
            "title": "TEST_Diary_Updated",
            "story": "Updated story content"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "TEST_Diary_Updated"
    
    def test_delete_diary_entry(self, auth_token, test_project_id, test_diary_id):
        """Test deleting a diary entry"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.delete(f"{BASE_URL}/api/projects/{test_project_id}/diary/{test_diary_id}", headers=headers)
        assert response.status_code == 200
        
        # Verify deletion
        get_response = requests.get(f"{BASE_URL}/api/projects/{test_project_id}/diary/{test_diary_id}", headers=headers)
        assert get_response.status_code == 404


class TestBlogCRUD:
    """Blog entries CRUD tests"""
    
    def test_create_blog_entry(self, auth_token, test_project_id):
        """Test creating a blog entry"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(f"{BASE_URL}/api/projects/{test_project_id}/blog", headers=headers, json={
            "title": "TEST_Blog_Entry",
            "description": "This is a test blog entry",
            "is_public": False
        })
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "TEST_Blog_Entry"
        assert "id" in data
        return data["id"]
    
    def test_list_blog_entries(self, auth_token, test_project_id):
        """Test listing blog entries"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/projects/{test_project_id}/blog", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "entries" in data
        assert "total" in data
    
    def test_update_blog_entry(self, auth_token, test_project_id, test_blog_id):
        """Test updating a blog entry"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.put(f"{BASE_URL}/api/projects/{test_project_id}/blog/{test_blog_id}", headers=headers, json={
            "title": "TEST_Blog_Updated",
            "description": "Updated blog content"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "TEST_Blog_Updated"
    
    def test_delete_blog_entry(self, auth_token, test_project_id, test_blog_id):
        """Test deleting a blog entry"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.delete(f"{BASE_URL}/api/projects/{test_project_id}/blog/{test_blog_id}", headers=headers)
        assert response.status_code == 200
        
        # Verify deletion
        get_response = requests.get(f"{BASE_URL}/api/projects/{test_project_id}/blog/{test_blog_id}", headers=headers)
        assert get_response.status_code == 404


class TestTasksCRUD:
    """Tasks CRUD tests"""
    
    def test_create_task(self, auth_token, test_project_id):
        """Test creating a task"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        task_datetime = datetime.now(timezone.utc).isoformat()
        response = requests.post(f"{BASE_URL}/api/projects/{test_project_id}/tasks", headers=headers, json={
            "title": "TEST_Task",
            "description": "Test task description",
            "task_datetime": task_datetime,
            "is_all_day": False,
            "recurrence": None
        })
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "TEST_Task"
        assert "id" in data
        return data["id"]
    
    def test_list_tasks(self, auth_token, test_project_id):
        """Test listing tasks"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/projects/{test_project_id}/tasks", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert "total" in data
    
    def test_update_task(self, auth_token, test_project_id, test_task_id):
        """Test updating a task"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.put(f"{BASE_URL}/api/projects/{test_project_id}/tasks/{test_task_id}", headers=headers, json={
            "title": "TEST_Task_Updated",
            "description": "Updated task description"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "TEST_Task_Updated"
    
    def test_delete_task(self, auth_token, test_project_id, test_task_id):
        """Test deleting a task"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.delete(f"{BASE_URL}/api/projects/{test_project_id}/tasks/{test_task_id}", headers=headers)
        assert response.status_code == 200
        
        # Verify deletion
        get_response = requests.get(f"{BASE_URL}/api/projects/{test_project_id}/tasks/{test_task_id}", headers=headers)
        assert get_response.status_code == 404


class TestRoutinesCRUD:
    """Routines CRUD tests"""
    
    def test_create_startup_routine(self, auth_token, test_project_id):
        """Test creating a startup routine task"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(f"{BASE_URL}/api/projects/{test_project_id}/routines/startup", headers=headers, json={
            "title": "TEST_Startup_Routine",
            "description": "Test startup routine"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "TEST_Startup_Routine"
        assert data["routine_type"] == "startup"
        return data["id"]
    
    def test_create_shutdown_routine(self, auth_token, test_project_id):
        """Test creating a shutdown routine task"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(f"{BASE_URL}/api/projects/{test_project_id}/routines/shutdown", headers=headers, json={
            "title": "TEST_Shutdown_Routine",
            "description": "Test shutdown routine"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "TEST_Shutdown_Routine"
        assert data["routine_type"] == "shutdown"
        return data["id"]
    
    def test_list_startup_routines(self, auth_token, test_project_id):
        """Test listing startup routines"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/projects/{test_project_id}/routines/startup", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert "completions_today" in data
    
    def test_list_shutdown_routines(self, auth_token, test_project_id):
        """Test listing shutdown routines"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/projects/{test_project_id}/routines/shutdown", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
    
    def test_complete_routine_task(self, auth_token, test_project_id, test_startup_routine_id):
        """Test completing a routine task"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(f"{BASE_URL}/api/projects/{test_project_id}/routines/startup/{test_startup_routine_id}/complete", headers=headers)
        assert response.status_code == 200
    
    def test_uncomplete_routine_task(self, auth_token, test_project_id, test_startup_routine_id):
        """Test uncompleting a routine task"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.delete(f"{BASE_URL}/api/projects/{test_project_id}/routines/startup/{test_startup_routine_id}/complete", headers=headers)
        assert response.status_code in [200, 404]  # 404 if not completed
    
    def test_delete_routine_task(self, auth_token, test_project_id, test_startup_routine_id):
        """Test deleting a routine task"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.delete(f"{BASE_URL}/api/projects/{test_project_id}/routines/startup/{test_startup_routine_id}", headers=headers)
        assert response.status_code == 200


class TestDashboard:
    """Dashboard endpoint tests"""
    
    def test_get_dashboard_data(self, auth_token):
        """Test getting dashboard data"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/dashboard/data", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "today_tasks" in data
        assert "incomplete_startup_tasks" in data
        assert "incomplete_shutdown_tasks" in data
        assert "projects_count" in data
        assert "date" in data
    
    def test_get_all_tasks(self, auth_token):
        """Test getting all tasks across projects"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/dashboard/all-tasks", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert "total" in data


class TestPublicEndpoints:
    """Public endpoints tests"""
    
    def test_list_public_projects(self):
        """Test listing public projects (no auth required)"""
        response = requests.get(f"{BASE_URL}/api/public/projects")
        assert response.status_code == 200
        data = response.json()
        assert "projects" in data
        assert "total" in data


class TestCleanup:
    """Cleanup test data"""
    
    def test_delete_test_project(self, auth_token, test_project_id):
        """Delete the test project and all related data"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.delete(f"{BASE_URL}/api/projects/{test_project_id}", headers=headers)
        assert response.status_code == 200
        
        # Verify deletion
        get_response = requests.get(f"{BASE_URL}/api/projects/{test_project_id}", headers=headers)
        assert get_response.status_code == 404


# Fixtures
@pytest.fixture(scope="session")
def auth_token():
    """Get authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Authentication failed - skipping authenticated tests")


@pytest.fixture(scope="session")
def test_project_id(auth_token):
    """Create a test project and return its ID"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = requests.post(f"{BASE_URL}/api/projects", headers=headers, json={
        "name": "TEST_Project_Fixture",
        "description": "Test project for fixtures",
        "is_public": False
    })
    if response.status_code == 200:
        project_id = response.json()["id"]
        yield project_id
        # Cleanup
        requests.delete(f"{BASE_URL}/api/projects/{project_id}", headers=headers)
    else:
        pytest.skip("Failed to create test project")


@pytest.fixture(scope="function")
def test_diary_id(auth_token, test_project_id):
    """Create a test diary entry and return its ID"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = requests.post(f"{BASE_URL}/api/projects/{test_project_id}/diary", headers=headers, json={
        "title": "TEST_Diary_Fixture",
        "story": "Test diary for fixture"
    })
    if response.status_code == 200:
        return response.json()["id"]
    pytest.skip("Failed to create test diary entry")


@pytest.fixture(scope="function")
def test_blog_id(auth_token, test_project_id):
    """Create a test blog entry and return its ID"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = requests.post(f"{BASE_URL}/api/projects/{test_project_id}/blog", headers=headers, json={
        "title": "TEST_Blog_Fixture",
        "description": "Test blog for fixture",
        "is_public": False
    })
    if response.status_code == 200:
        return response.json()["id"]
    pytest.skip("Failed to create test blog entry")


@pytest.fixture(scope="function")
def test_task_id(auth_token, test_project_id):
    """Create a test task and return its ID"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    task_datetime = datetime.now(timezone.utc).isoformat()
    response = requests.post(f"{BASE_URL}/api/projects/{test_project_id}/tasks", headers=headers, json={
        "title": "TEST_Task_Fixture",
        "description": "Test task for fixture",
        "task_datetime": task_datetime,
        "is_all_day": False
    })
    if response.status_code == 200:
        return response.json()["id"]
    pytest.skip("Failed to create test task")


@pytest.fixture(scope="function")
def test_startup_routine_id(auth_token, test_project_id):
    """Create a test startup routine and return its ID"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = requests.post(f"{BASE_URL}/api/projects/{test_project_id}/routines/startup", headers=headers, json={
        "title": "TEST_Startup_Fixture",
        "description": "Test startup routine for fixture"
    })
    if response.status_code == 200:
        return response.json()["id"]
    pytest.skip("Failed to create test startup routine")
