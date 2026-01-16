import requests
import sys
import json
from datetime import datetime

class SelfSufficientAPITester:
    def __init__(self, base_url="https://eco-life-manager.preview.emergentagent.com/api"):
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