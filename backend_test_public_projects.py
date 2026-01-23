import requests
import sys
import json
from datetime import datetime

class PublicProjectsTester:
    def __init__(self, base_url="https://lifesteward-1.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    return success, response_data
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_public_projects_list(self):
        """Test public projects listing"""
        print("\n=== PUBLIC PROJECTS LIST TESTS ===")
        
        # Test basic public projects endpoint
        success1, response = self.run_test("List Public Projects", "GET", "public/projects", 200)
        
        projects = []
        if success1:
            projects = response.get('projects', [])
            print(f"   Found {len(projects)} public projects")
            
            # Check if Community Garden exists
            community_garden = None
            for project in projects:
                print(f"   - {project.get('name', 'Unknown')}")
                if 'Community Garden' in project.get('name', ''):
                    community_garden = project
                    print(f"     ✅ Found Community Garden project: {project['id']}")
            
            if not community_garden:
                print("   ❌ Community Garden project not found")
                return False
        
        return success1

    def test_public_projects_search(self):
        """Test public projects search functionality"""
        print("\n=== PUBLIC PROJECTS SEARCH TESTS ===")
        
        # Test search with 'garden' keyword
        success1, response = self.run_test(
            "Search Public Projects - 'garden'", 
            "GET", 
            "public/projects?search=garden", 
            200
        )
        
        if success1:
            projects = response.get('projects', [])
            print(f"   Found {len(projects)} projects matching 'garden'")
            
            # Should find Community Garden
            found_community_garden = any('Community Garden' in p.get('name', '') for p in projects)
            if found_community_garden:
                print("   ✅ Community Garden found in search results")
            else:
                print("   ❌ Community Garden not found in search results")
                return False
        
        # Test search with non-existent term
        success2, response = self.run_test(
            "Search Public Projects - 'nonexistent'", 
            "GET", 
            "public/projects?search=nonexistent", 
            200
        )
        
        if success2:
            projects = response.get('projects', [])
            print(f"   Found {len(projects)} projects matching 'nonexistent'")
        
        return success1 and success2

    def test_public_project_detail(self):
        """Test public project detail endpoint"""
        print("\n=== PUBLIC PROJECT DETAIL TESTS ===")
        
        # First get the list to find a project ID
        success, response = self.run_test("Get Projects for Detail Test", "GET", "public/projects", 200)
        
        if not success or not response.get('projects'):
            print("   ❌ No public projects found for detail testing")
            return False
        
        project_id = response['projects'][0]['id']
        project_name = response['projects'][0]['name']
        
        # Test getting project detail
        success1, project_detail = self.run_test(
            f"Get Public Project Detail - {project_name}", 
            "GET", 
            f"public/projects/{project_id}", 
            200
        )
        
        if success1:
            print(f"   Project Name: {project_detail.get('name', 'Unknown')}")
            print(f"   Project Description: {project_detail.get('description', 'No description')[:100]}...")
            print(f"   Is Public: {project_detail.get('is_public', False)}")
        
        return success1

    def test_public_project_blog(self):
        """Test public project blog endpoints"""
        print("\n=== PUBLIC PROJECT BLOG TESTS ===")
        
        # First get a public project
        success, response = self.run_test("Get Projects for Blog Test", "GET", "public/projects", 200)
        
        if not success or not response.get('projects'):
            print("   ❌ No public projects found for blog testing")
            return False
        
        project_id = response['projects'][0]['id']
        project_name = response['projects'][0]['name']
        
        # Test getting blog entries
        success1, blog_response = self.run_test(
            f"Get Public Project Blog - {project_name}", 
            "GET", 
            f"public/projects/{project_id}/blog", 
            200
        )
        
        if success1:
            entries = blog_response.get('entries', [])
            print(f"   Found {len(entries)} public blog entries")
            
            # If there are blog entries, test getting one
            if entries:
                entry_id = entries[0]['id']
                success2, entry_detail = self.run_test(
                    f"Get Public Blog Entry Detail", 
                    "GET", 
                    f"public/projects/{project_id}/blog/{entry_id}", 
                    200
                )
                
                if success2:
                    print(f"   Blog Entry Title: {entry_detail.get('title', 'Unknown')}")
                
                return success1 and success2
        
        return success1

    def test_public_project_library(self):
        """Test public project library endpoints"""
        print("\n=== PUBLIC PROJECT LIBRARY TESTS ===")
        
        # First get a public project
        success, response = self.run_test("Get Projects for Library Test", "GET", "public/projects", 200)
        
        if not success or not response.get('projects'):
            print("   ❌ No public projects found for library testing")
            return False
        
        project_id = response['projects'][0]['id']
        project_name = response['projects'][0]['name']
        
        # Test getting library entries
        success1, library_response = self.run_test(
            f"Get Public Project Library - {project_name}", 
            "GET", 
            f"public/projects/{project_id}/library", 
            200
        )
        
        if success1:
            entries = library_response.get('entries', [])
            print(f"   Found {len(entries)} public library entries")
            
            # If there are library entries, test getting one
            if entries:
                entry_id = entries[0]['id']
                success2, entry_detail = self.run_test(
                    f"Get Public Library Entry Detail", 
                    "GET", 
                    f"public/projects/{project_id}/library/entries/{entry_id}", 
                    200
                )
                
                if success2:
                    print(f"   Library Entry Title: {entry_detail.get('title', 'Unknown')}")
                
                return success1 and success2
        
        return success1

def main():
    print("🚀 Starting Public Projects API Tests")
    print("=" * 50)
    
    tester = PublicProjectsTester()
    
    # Run all test suites
    test_results = []
    
    test_results.append(("Public Projects List", tester.test_public_projects_list()))
    test_results.append(("Public Projects Search", tester.test_public_projects_search()))
    test_results.append(("Public Project Detail", tester.test_public_project_detail()))
    test_results.append(("Public Project Blog", tester.test_public_project_blog()))
    test_results.append(("Public Project Library", tester.test_public_project_library()))
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
    
    print(f"\nOverall: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    # Return appropriate exit code
    all_passed = all(result for _, result in test_results)
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())