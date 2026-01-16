import requests
import sys
import json
from datetime import datetime

class SelfSufficientAPITester:
    def __init__(self, base_url="https://homestead-hub-2.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_email = "admin@selfsufficient.app"
        self.admin_password = "admin123"

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                except:
                    print(f"   Response: {response.text[:100]}...")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")

            return success, response.json() if response.text and response.status_code < 500 else {}

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed - Network Error: {str(e)}")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test basic health endpoints"""
        print("\n=== HEALTH CHECK TESTS ===")
        
        # Test root endpoint
        success1, _ = self.run_test("Root Endpoint", "GET", "", 200)
        
        # Test health endpoint
        success2, _ = self.run_test("Health Check", "GET", "health", 200)
        
        return success1 and success2

    def test_admin_seeding(self):
        """Test admin user seeding"""
        print("\n=== ADMIN SEEDING TESTS ===")
        
        # Try to seed admin (should fail if already exists)
        success, response = self.run_test("Seed Admin User", "POST", "seed/admin", 400)
        
        # If it returns 200, admin was created successfully
        if not success:
            success, response = self.run_test("Seed Admin User (First Time)", "POST", "seed/admin", 200)
        
        return True  # Either way is acceptable

    def test_login(self):
        """Test login functionality"""
        print("\n=== LOGIN TESTS ===")
        
        # Test with correct credentials
        success, response = self.run_test(
            "Login with Admin Credentials",
            "POST",
            "auth/login",
            200,
            data={"email": self.admin_email, "password": self.admin_password}
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            print(f"   Token obtained: {self.token[:20]}...")
            return True
        
        # Test with wrong credentials
        self.run_test(
            "Login with Wrong Credentials",
            "POST", 
            "auth/login",
            401,
            data={"email": "wrong@email.com", "password": "wrongpass"}
        )
        
        return success

    def test_protected_routes(self):
        """Test protected routes"""
        print("\n=== PROTECTED ROUTE TESTS ===")
        
        if not self.token:
            print("❌ No token available for protected route testing")
            return False
        
        # Test /auth/me endpoint
        success, response = self.run_test("Get Current User", "GET", "auth/me", 200)
        
        if success:
            print(f"   User data: {response}")
        
        return success

    def test_forgot_password(self):
        """Test forgot password functionality"""
        print("\n=== FORGOT PASSWORD TESTS ===")
        
        # Test forgot password with valid email
        success1, _ = self.run_test(
            "Forgot Password - Valid Email",
            "POST",
            "auth/forgot-password",
            200,
            data={"email": self.admin_email}
        )
        
        # Test forgot password with invalid email
        success2, _ = self.run_test(
            "Forgot Password - Invalid Email",
            "POST",
            "auth/forgot-password", 
            200,  # Should return 200 for security reasons
            data={"email": "nonexistent@email.com"}
        )
        
        return success1 and success2

    def test_admin_routes(self):
        """Test admin-only routes"""
        print("\n=== ADMIN ROUTE TESTS ===")
        
        if not self.token:
            print("❌ No token available for admin route testing")
            return False
        
        # Test list users (admin only)
        success1, response = self.run_test("List Users (Admin)", "GET", "admin/users", 200)
        
        if success1:
            print(f"   Found {len(response)} users")
        
        # Test create user (admin only)
        test_user_data = {
            "name": "Test User",
            "email": f"testuser_{datetime.now().strftime('%H%M%S')}@test.com",
            "password": "testpass123",
            "is_admin": False
        }
        
        success2, user_response = self.run_test(
            "Create User (Admin)", 
            "POST", 
            "admin/users", 
            200, 
            data=test_user_data
        )
        
        created_user_id = None
        if success2 and 'id' in user_response:
            created_user_id = user_response['id']
            print(f"   Created user with ID: {created_user_id}")
        
        # Test delete user (admin only) - only if we created one
        success3 = True
        if created_user_id:
            success3, _ = self.run_test(
                "Delete User (Admin)", 
                "DELETE", 
                f"admin/users/{created_user_id}", 
                200
            )
        
        return success1 and success2 and success3

    def test_unauthorized_access(self):
        """Test unauthorized access to protected routes"""
        print("\n=== UNAUTHORIZED ACCESS TESTS ===")
        
        # Temporarily remove token
        original_token = self.token
        self.token = None
        
        # Test accessing protected route without token
        success1, _ = self.run_test("Access /auth/me without token", "GET", "auth/me", 401)
        
        # Test with invalid token
        self.token = "invalid_token"
        success2, _ = self.run_test("Access /auth/me with invalid token", "GET", "auth/me", 401)
        
        # Restore original token
        self.token = original_token
        
        return success1 and success2

    def test_projects_crud(self):
        """Test project CRUD operations"""
        print("\n=== PROJECT CRUD TESTS ===")
        
        if not self.token:
            print("❌ No token available for project testing")
            return False
        
        # Test create project
        project_data = {
            "name": f"Test Project {datetime.now().strftime('%H%M%S')}",
            "description": "This is a test project for automated testing",
            "is_public": False
        }
        
        success1, project_response = self.run_test(
            "Create Project", 
            "POST", 
            "projects", 
            200, 
            data=project_data
        )
        
        project_id = None
        if success1 and 'id' in project_response:
            project_id = project_response['id']
            print(f"   Created project with ID: {project_id}")
        
        # Test list projects
        success2, projects_response = self.run_test("List Projects", "GET", "projects", 200)
        
        if success2:
            print(f"   Found {projects_response.get('total', 0)} projects")
        
        # Test get specific project
        success3 = True
        if project_id:
            success3, _ = self.run_test(
                "Get Project by ID", 
                "GET", 
                f"projects/{project_id}", 
                200
            )
        
        # Test update project
        success4 = True
        if project_id:
            update_data = {
                "name": f"Updated Test Project {datetime.now().strftime('%H%M%S')}",
                "description": "Updated description",
                "is_public": True
            }
            success4, _ = self.run_test(
                "Update Project", 
                "PUT", 
                f"projects/{project_id}", 
                200, 
                data=update_data
            )
        
        # Test search projects
        success5, _ = self.run_test(
            "Search Projects", 
            "GET", 
            "projects?search=Test&sort_by=name&sort_order=asc", 
            200
        )
        
        # Test delete project (cleanup)
        success6 = True
        if project_id:
            success6, _ = self.run_test(
                "Delete Project", 
                "DELETE", 
                f"projects/{project_id}", 
                200
            )
        
        return success1 and success2 and success3 and success4 and success5 and success6

    def test_public_projects(self):
        """Test public projects API"""
        print("\n=== PUBLIC PROJECTS TESTS ===")
        
        # Test public projects endpoint (no auth required)
        original_token = self.token
        self.token = None
        
        success1, response = self.run_test("List Public Projects", "GET", "public/projects", 200)
        
        if success1:
            print(f"   Found {response.get('total', 0)} public projects")
        
        # Test public projects with search
        success2, _ = self.run_test(
            "Search Public Projects", 
            "GET", 
            "public/projects?search=garden&sort_by=created_at&sort_order=desc", 
            200
        )
        
        # Restore token
        self.token = original_token
        
        return success1 and success2

    def test_change_password(self):
        """Test change password functionality"""
        print("\n=== CHANGE PASSWORD TESTS ===")
        
        if not self.token:
            print("❌ No token available for password change testing")
            return False
        
        # Test change password with wrong current password
        success1, _ = self.run_test(
            "Change Password - Wrong Current", 
            "POST", 
            "auth/change-password", 
            400,
            data={
                "current_password": "wrongpassword",
                "new_password": "newpassword123"
            }
        )
        
        # Test change password with correct current password
        success2, _ = self.run_test(
            "Change Password - Correct Current", 
            "POST", 
            "auth/change-password", 
            200,
            data={
                "current_password": self.admin_password,
                "new_password": "newpassword123"
            }
        )
        
        # Change password back to original
        success3 = True
        if success2:
            success3, _ = self.run_test(
                "Change Password Back", 
                "POST", 
                "auth/change-password", 
                200,
                data={
                    "current_password": "newpassword123",
                    "new_password": self.admin_password
                }
            )
        
        return success1 and success2 and success3

    def test_tasks_crud(self):
        """Test task CRUD operations"""
        print("\n=== TASK CRUD TESTS ===")
        
        if not self.token:
            print("❌ No token available for task testing")
            return False
        
        # First create a project for tasks
        project_data = {
            "name": f"Task Test Project {datetime.now().strftime('%H%M%S')}",
            "description": "Project for testing tasks",
            "is_public": False
        }
        
        success_proj, project_response = self.run_test(
            "Create Project for Tasks", 
            "POST", 
            "projects", 
            200, 
            data=project_data
        )
        
        if not success_proj or 'id' not in project_response:
            print("❌ Failed to create project for task testing")
            return False
        
        project_id = project_response['id']
        
        # Test create task
        task_data = {
            "title": "Water garden",
            "description": "Daily watering of vegetables",
            "task_datetime": "2024-12-20T09:00:00",
            "is_all_day": False,
            "recurrence": "daily"
        }
        
        success1, task_response = self.run_test(
            "Create Task", 
            "POST", 
            f"projects/{project_id}/tasks", 
            200, 
            data=task_data
        )
        
        task_id = None
        if success1 and 'id' in task_response:
            task_id = task_response['id']
            print(f"   Created task with ID: {task_id}")
        
        # Test list tasks
        success2, tasks_response = self.run_test(
            "List Tasks", 
            "GET", 
            f"projects/{project_id}/tasks", 
            200
        )
        
        if success2:
            print(f"   Found {tasks_response.get('total', 0)} tasks")
        
        # Test get specific task
        success3 = True
        if task_id:
            success3, _ = self.run_test(
                "Get Task by ID", 
                "GET", 
                f"projects/{project_id}/tasks/{task_id}", 
                200
            )
        
        # Test update task
        success4 = True
        if task_id:
            update_data = {
                "title": "Water garden (updated)",
                "description": "Updated description",
                "recurrence": "weekly"
            }
            success4, _ = self.run_test(
                "Update Task", 
                "PUT", 
                f"projects/{project_id}/tasks/{task_id}", 
                200, 
                data=update_data
            )
        
        # Test delete task
        success5 = True
        if task_id:
            success5, _ = self.run_test(
                "Delete Task", 
                "DELETE", 
                f"projects/{project_id}/tasks/{task_id}", 
                200
            )
        
        # Cleanup project
        self.run_test("Delete Task Test Project", "DELETE", f"projects/{project_id}", 200)
        
        return success1 and success2 and success3 and success4 and success5

    def test_routines_crud(self):
        """Test routine CRUD operations"""
        print("\n=== ROUTINE CRUD TESTS ===")
        
        if not self.token:
            print("❌ No token available for routine testing")
            return False
        
        # First create a project for routines
        project_data = {
            "name": f"Routine Test Project {datetime.now().strftime('%H%M%S')}",
            "description": "Project for testing routines",
            "is_public": False
        }
        
        success_proj, project_response = self.run_test(
            "Create Project for Routines", 
            "POST", 
            "projects", 
            200, 
            data=project_data
        )
        
        if not success_proj or 'id' not in project_response:
            print("❌ Failed to create project for routine testing")
            return False
        
        project_id = project_response['id']
        
        # Test create startup routine task
        startup_task_data = {
            "title": "Check animals",
            "description": "Check on chickens and goats",
            "order": 0
        }
        
        success1, startup_response = self.run_test(
            "Create Startup Routine Task", 
            "POST", 
            f"projects/{project_id}/routines/startup", 
            200, 
            data=startup_task_data
        )
        
        startup_task_id = None
        if success1 and 'id' in startup_response:
            startup_task_id = startup_response['id']
            print(f"   Created startup task with ID: {startup_task_id}")
        
        # Test create shutdown routine task
        shutdown_task_data = {
            "title": "Lock gates",
            "description": "Secure all gates and doors",
            "order": 0
        }
        
        success2, shutdown_response = self.run_test(
            "Create Shutdown Routine Task", 
            "POST", 
            f"projects/{project_id}/routines/shutdown", 
            200, 
            data=shutdown_task_data
        )
        
        shutdown_task_id = None
        if success2 and 'id' in shutdown_response:
            shutdown_task_id = shutdown_response['id']
            print(f"   Created shutdown task with ID: {shutdown_task_id}")
        
        # Test list startup routines
        success3, startup_list = self.run_test(
            "List Startup Routines", 
            "GET", 
            f"projects/{project_id}/routines/startup", 
            200
        )
        
        if success3:
            print(f"   Found {len(startup_list.get('tasks', []))} startup tasks")
        
        # Test list shutdown routines
        success4, shutdown_list = self.run_test(
            "List Shutdown Routines", 
            "GET", 
            f"projects/{project_id}/routines/shutdown", 
            200
        )
        
        if success4:
            print(f"   Found {len(shutdown_list.get('tasks', []))} shutdown tasks")
        
        # Test toggle completion
        success5 = True
        if startup_task_id:
            success5, _ = self.run_test(
                "Toggle Startup Task Completion", 
                "POST", 
                f"projects/{project_id}/routines/startup/{startup_task_id}/complete", 
                200
            )
        
        success6 = True
        if shutdown_task_id:
            success6, _ = self.run_test(
                "Toggle Shutdown Task Completion", 
                "POST", 
                f"projects/{project_id}/routines/shutdown/{shutdown_task_id}/complete", 
                200
            )
        
        # Test update routine task
        success7 = True
        if startup_task_id:
            update_data = {
                "title": "Check animals (updated)",
                "description": "Updated description"
            }
            success7, _ = self.run_test(
                "Update Startup Routine Task", 
                "PUT", 
                f"projects/{project_id}/routines/startup/{startup_task_id}", 
                200, 
                data=update_data
            )
        
        # Test delete routine tasks
        success8 = True
        if startup_task_id:
            success8, _ = self.run_test(
                "Delete Startup Routine Task", 
                "DELETE", 
                f"projects/{project_id}/routines/startup/{startup_task_id}", 
                200
            )
        
        success9 = True
        if shutdown_task_id:
            success9, _ = self.run_test(
                "Delete Shutdown Routine Task", 
                "DELETE", 
                f"projects/{project_id}/routines/shutdown/{shutdown_task_id}", 
                200
            )
        
        # Cleanup project
        self.run_test("Delete Routine Test Project", "DELETE", f"projects/{project_id}", 200)
        
        return success1 and success2 and success3 and success4 and success5 and success6 and success7 and success8 and success9

    def test_dashboard_today(self):
        """Test dashboard today endpoint"""
        print("\n=== DASHBOARD TODAY TESTS ===")
        
        if not self.token:
            print("❌ No token available for dashboard testing")
            return False
        
        # Test dashboard/today endpoint
        success, response = self.run_test(
            "Get Dashboard Today Data", 
            "GET", 
            "dashboard/today", 
            200
        )
        
        if success:
            print(f"   Today tasks: {len(response.get('today_tasks', []))}")
            print(f"   Startup tasks: {len(response.get('startup_tasks', []))}")
            print(f"   Shutdown tasks: {len(response.get('shutdown_tasks', []))}")
            print(f"   Startup completions: {len(response.get('startup_completions', []))}")
            print(f"   Shutdown completions: {len(response.get('shutdown_completions', []))}")
        
        return success

def main():
    print("🚀 Starting Self-Sufficient Lifestyle App API Tests")
    print("=" * 60)
    
    tester = SelfSufficientAPITester()
    
    # Run all test suites
    test_results = []
    
    test_results.append(("Health Check", tester.test_health_check()))
    test_results.append(("Admin Seeding", tester.test_admin_seeding()))
    test_results.append(("Login", tester.test_login()))
    test_results.append(("Protected Routes", tester.test_protected_routes()))
    test_results.append(("Forgot Password", tester.test_forgot_password()))
    test_results.append(("Admin Routes", tester.test_admin_routes()))
    test_results.append(("Projects CRUD", tester.test_projects_crud()))
    test_results.append(("Tasks CRUD", tester.test_tasks_crud()))
    test_results.append(("Routines CRUD", tester.test_routines_crud()))
    test_results.append(("Dashboard Today", tester.test_dashboard_today()))
    test_results.append(("Public Projects", tester.test_public_projects()))
    test_results.append(("Change Password", tester.test_change_password()))
    test_results.append(("Unauthorized Access", tester.test_unauthorized_access()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
    
    print(f"\nOverall: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    # Return appropriate exit code
    all_passed = all(result for _, result in test_results)
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())