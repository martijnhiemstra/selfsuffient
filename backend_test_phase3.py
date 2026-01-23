#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import uuid

class Phase3APITester:
    def __init__(self, base_url="https://lifesteward-1.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.project_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                if files:
                    # Remove Content-Type for file uploads
                    headers.pop('Content-Type', None)
                    response = requests.post(url, files=files, data=data, headers=headers)
                else:
                    response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            details = f"Status: {response.status_code}"
            
            if not success:
                try:
                    error_detail = response.json().get('detail', 'Unknown error')
                    details += f", Error: {error_detail}"
                except:
                    details += f", Response: {response.text[:100]}"
            
            self.log_test(name, success, details)
            
            if success and response.content:
                try:
                    return success, response.json()
                except:
                    return success, {}
            
            return success, response.json() if success and response.content else {}

        except Exception as e:
            self.log_test(name, False, f"Exception: {str(e)}")
            return False, {}

    def setup_auth_and_project(self):
        """Login and get/create a test project"""
        print("🔧 Setting up authentication and test project...")
        
        # Login
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "auth/login",
            200,
            {"email": "admin@selfsufficient.app", "password": "admin123"}
        )
        
        if not success:
            print("❌ Failed to login - cannot continue tests")
            return False
            
        self.token = response.get('access_token')
        
        # Get existing projects
        success, response = self.run_test(
            "List Projects",
            "GET", 
            "projects",
            200
        )
        
        if success and response.get('projects'):
            self.project_id = response['projects'][0]['id']
            print(f"📁 Using existing project: {self.project_id}")
        else:
            # Create test project
            success, response = self.run_test(
                "Create Test Project",
                "POST",
                "projects", 
                200,
                {"name": "Phase 3 Test Project", "description": "Testing Phase 3 features"}
            )
            if success:
                self.project_id = response['id']
                print(f"📁 Created test project: {self.project_id}")
            else:
                print("❌ Failed to create test project")
                return False
        
        return True

    def test_diary_features(self):
        """Test diary CRUD operations"""
        print("\n📖 Testing Diary Features...")
        
        # Create diary entry
        diary_data = {
            "title": "Test Diary Entry",
            "story": "<p>This is a <strong>rich text</strong> diary entry with <em>formatting</em>.</p>",
            "entry_datetime": datetime.now().isoformat()
        }
        
        success, response = self.run_test(
            "Create Diary Entry",
            "POST",
            f"projects/{self.project_id}/diary",
            200,
            diary_data
        )
        
        if not success:
            return False
            
        diary_id = response['id']
        
        # List diary entries
        success, response = self.run_test(
            "List Diary Entries",
            "GET",
            f"projects/{self.project_id}/diary",
            200
        )
        
        # Get specific diary entry
        success, response = self.run_test(
            "Get Diary Entry",
            "GET",
            f"projects/{self.project_id}/diary/{diary_id}",
            200
        )
        
        # Update diary entry
        update_data = {
            "title": "Updated Diary Entry",
            "story": "<p>Updated content with more <u>formatting</u>.</p>"
        }
        
        success, response = self.run_test(
            "Update Diary Entry",
            "PUT",
            f"projects/{self.project_id}/diary/{diary_id}",
            200,
            update_data
        )
        
        # Search diary entries
        success, response = self.run_test(
            "Search Diary Entries",
            "GET",
            f"projects/{self.project_id}/diary?search=Updated",
            200
        )
        
        # Delete diary entry
        success, response = self.run_test(
            "Delete Diary Entry",
            "DELETE",
            f"projects/{self.project_id}/diary/{diary_id}",
            200
        )
        
        return True

    def test_gallery_features(self):
        """Test gallery folder and image operations"""
        print("\n🖼️ Testing Gallery Features...")
        
        # Create gallery folder
        folder_data = {"name": "Test Gallery Folder"}
        
        success, response = self.run_test(
            "Create Gallery Folder",
            "POST",
            f"projects/{self.project_id}/gallery/folders",
            200,
            folder_data
        )
        
        if not success:
            return False
            
        folder_id = response['id']
        
        # Create subfolder
        subfolder_data = {
            "name": "Test Subfolder",
            "parent_id": folder_id
        }
        
        success, response = self.run_test(
            "Create Gallery Subfolder",
            "POST",
            f"projects/{self.project_id}/gallery/folders",
            200,
            subfolder_data
        )
        
        subfolder_id = response['id'] if success else None
        
        # List gallery contents
        success, response = self.run_test(
            "List Gallery Contents",
            "GET",
            f"projects/{self.project_id}/gallery",
            200
        )
        
        # List contents in folder
        success, response = self.run_test(
            "List Gallery Folder Contents",
            "GET",
            f"projects/{self.project_id}/gallery?folder_id={folder_id}",
            200
        )
        
        # Update folder
        update_data = {"name": "Updated Gallery Folder"}
        success, response = self.run_test(
            "Update Gallery Folder",
            "PUT",
            f"projects/{self.project_id}/gallery/folders/{folder_id}",
            200,
            update_data
        )
        
        # Delete subfolder first (if created)
        if subfolder_id:
            success, response = self.run_test(
                "Delete Gallery Subfolder",
                "DELETE",
                f"projects/{self.project_id}/gallery/folders/{subfolder_id}",
                200
            )
        
        # Delete main folder
        success, response = self.run_test(
            "Delete Gallery Folder",
            "DELETE",
            f"projects/{self.project_id}/gallery/folders/{folder_id}",
            200
        )
        
        return True

    def test_blog_features(self):
        """Test blog CRUD operations"""
        print("\n📝 Testing Blog Features...")
        
        # Create blog entry
        blog_data = {
            "title": "Test Blog Post",
            "description": "<p>This is a <strong>public blog post</strong> with rich content.</p>",
            "is_public": True
        }
        
        success, response = self.run_test(
            "Create Blog Entry",
            "POST",
            f"projects/{self.project_id}/blog",
            200,
            blog_data
        )
        
        if not success:
            return False
            
        blog_id = response['id']
        
        # List blog entries
        success, response = self.run_test(
            "List Blog Entries",
            "GET",
            f"projects/{self.project_id}/blog",
            200
        )
        
        # Get specific blog entry
        success, response = self.run_test(
            "Get Blog Entry",
            "GET",
            f"projects/{self.project_id}/blog/{blog_id}",
            200
        )
        
        # Update blog entry
        update_data = {
            "title": "Updated Blog Post",
            "description": "<p>Updated blog content.</p>",
            "is_public": False
        }
        
        success, response = self.run_test(
            "Update Blog Entry",
            "PUT",
            f"projects/{self.project_id}/blog/{blog_id}",
            200,
            update_data
        )
        
        # Search blog entries
        success, response = self.run_test(
            "Search Blog Entries",
            "GET",
            f"projects/{self.project_id}/blog?search=Updated",
            200
        )
        
        # Test public blog access (should fail for private entry)
        success, response = self.run_test(
            "Access Private Blog Entry Publicly",
            "GET",
            f"public/projects/{self.project_id}/blog/{blog_id}",
            404  # Should not be accessible
        )
        
        # Make it public again for public access test
        success, response = self.run_test(
            "Make Blog Entry Public",
            "PUT",
            f"projects/{self.project_id}/blog/{blog_id}",
            200,
            {"is_public": True}
        )
        
        # Test public blog access (should work now)
        success, response = self.run_test(
            "Access Public Blog Entry",
            "GET",
            f"public/projects/{self.project_id}/blog/{blog_id}",
            200
        )
        
        # Delete blog entry
        success, response = self.run_test(
            "Delete Blog Entry",
            "DELETE",
            f"projects/{self.project_id}/blog/{blog_id}",
            200
        )
        
        return True

    def test_library_features(self):
        """Test library folder and entry operations"""
        print("\n📚 Testing Library Features...")
        
        # Create library folder
        folder_data = {"name": "Test Library Folder"}
        
        success, response = self.run_test(
            "Create Library Folder",
            "POST",
            f"projects/{self.project_id}/library/folders",
            200,
            folder_data
        )
        
        if not success:
            return False
            
        folder_id = response['id']
        
        # Create library entry
        entry_data = {
            "title": "Test Library Entry",
            "description": "<p>This is a <strong>library entry</strong> with knowledge.</p>",
            "folder_id": folder_id,
            "is_public": True
        }
        
        success, response = self.run_test(
            "Create Library Entry",
            "POST",
            f"projects/{self.project_id}/library/entries",
            200,
            entry_data
        )
        
        if not success:
            return False
            
        entry_id = response['id']
        
        # List library contents
        success, response = self.run_test(
            "List Library Contents",
            "GET",
            f"projects/{self.project_id}/library",
            200
        )
        
        # List contents in folder
        success, response = self.run_test(
            "List Library Folder Contents",
            "GET",
            f"projects/{self.project_id}/library?folder_id={folder_id}",
            200
        )
        
        # Get specific library entry
        success, response = self.run_test(
            "Get Library Entry",
            "GET",
            f"projects/{self.project_id}/library/entries/{entry_id}",
            200
        )
        
        # Update library entry
        update_data = {
            "title": "Updated Library Entry",
            "description": "<p>Updated library content.</p>",
            "is_public": False
        }
        
        success, response = self.run_test(
            "Update Library Entry",
            "PUT",
            f"projects/{self.project_id}/library/entries/{entry_id}",
            200,
            update_data
        )
        
        # Search library entries
        success, response = self.run_test(
            "Search Library Contents",
            "GET",
            f"projects/{self.project_id}/library?search=Updated",
            200
        )
        
        # Test public library access
        success, response = self.run_test(
            "Access Public Library Contents",
            "GET",
            f"public/projects/{self.project_id}/library",
            200
        )
        
        # Delete library entry
        success, response = self.run_test(
            "Delete Library Entry",
            "DELETE",
            f"projects/{self.project_id}/library/entries/{entry_id}",
            200
        )
        
        # Delete library folder
        success, response = self.run_test(
            "Delete Library Folder",
            "DELETE",
            f"projects/{self.project_id}/library/folders/{folder_id}",
            200
        )
        
        return True

    def run_all_tests(self):
        """Run all Phase 3 tests"""
        print("🚀 Starting Phase 3 API Testing...")
        print("=" * 50)
        
        if not self.setup_auth_and_project():
            return False
        
        # Run all feature tests
        self.test_diary_features()
        self.test_gallery_features() 
        self.test_blog_features()
        self.test_library_features()
        
        # Print summary
        print("\n" + "=" * 50)
        if self.tests_run > 0:
            print(f"📊 Phase 3 Test Results: {self.tests_passed}/{self.tests_run} passed")
            print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        else:
            print("📊 No tests were executed")
        
        if self.tests_passed == self.tests_run and self.tests_run > 0:
            print("🎉 All Phase 3 API tests passed!")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            return False

def main():
    tester = Phase3APITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())