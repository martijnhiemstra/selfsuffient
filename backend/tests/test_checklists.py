"""
Checklist API Tests - Testing CRUD operations for checklists and checklist items
Tests the nested checklist feature within projects
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "admin@selfsufficient.app"
TEST_PASSWORD = "admin123"


class TestChecklistAPI:
    """Test checklist CRUD operations"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login to get token
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        if login_response.status_code != 200:
            pytest.skip(f"Authentication failed: {login_response.status_code}")
        
        token = login_response.json().get("token")
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        # Get a project to use for testing
        projects_response = self.session.get(f"{BASE_URL}/api/projects")
        if projects_response.status_code != 200:
            pytest.skip("Failed to get projects")
        
        projects = projects_response.json().get("projects", [])
        if not projects:
            pytest.skip("No projects available for testing")
        
        # Use first project (Backyard Garden or any available)
        self.project_id = projects[0]["id"]
        self.project_name = projects[0]["name"]
        print(f"Using project: {self.project_name} (ID: {self.project_id})")
        
        yield
        
        # Cleanup: Delete test checklists created during tests
        self._cleanup_test_data()
    
    def _cleanup_test_data(self):
        """Clean up test data after tests"""
        try:
            # Get all checklists for the project
            response = self.session.get(f"{BASE_URL}/api/checklists?project_id={self.project_id}")
            if response.status_code == 200:
                checklists = response.json().get("checklists", [])
                for checklist in checklists:
                    if checklist["name"].startswith("TEST_"):
                        self.session.delete(f"{BASE_URL}/api/checklists/{checklist['id']}")
        except Exception as e:
            print(f"Cleanup error: {e}")
    
    # ============ CHECKLIST CRUD TESTS ============
    
    def test_01_list_checklists_empty_or_existing(self):
        """Test listing checklists for a project"""
        response = self.session.get(f"{BASE_URL}/api/checklists?project_id={self.project_id}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "checklists" in data, "Response should contain 'checklists' key"
        assert "total" in data, "Response should contain 'total' key"
        assert isinstance(data["checklists"], list), "Checklists should be a list"
        
        print(f"Found {data['total']} existing checklists")
    
    def test_02_create_checklist(self):
        """Test creating a new checklist"""
        checklist_data = {
            "project_id": self.project_id,
            "name": "TEST_Daily Farm Tasks",
            "description": "Daily tasks for the farm"
        }
        
        response = self.session.post(f"{BASE_URL}/api/checklists", json=checklist_data)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["name"] == checklist_data["name"], "Name should match"
        assert data["description"] == checklist_data["description"], "Description should match"
        assert data["project_id"] == self.project_id, "Project ID should match"
        assert "id" in data, "Response should contain 'id'"
        assert data["total_items"] == 0, "New checklist should have 0 items"
        assert data["completed_items"] == 0, "New checklist should have 0 completed items"
        
        # Store for later tests
        self.created_checklist_id = data["id"]
        print(f"Created checklist: {data['name']} (ID: {data['id']})")
    
    def test_03_get_checklist(self):
        """Test getting a single checklist"""
        # First create a checklist
        checklist_data = {
            "project_id": self.project_id,
            "name": "TEST_Get Checklist Test",
            "description": "Test description"
        }
        create_response = self.session.post(f"{BASE_URL}/api/checklists", json=checklist_data)
        assert create_response.status_code == 200
        checklist_id = create_response.json()["id"]
        
        # Now get it
        response = self.session.get(f"{BASE_URL}/api/checklists/{checklist_id}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["id"] == checklist_id, "ID should match"
        assert data["name"] == checklist_data["name"], "Name should match"
        assert "items" in data, "Response should contain 'items'"
        assert isinstance(data["items"], list), "Items should be a list"
        
        print(f"Retrieved checklist: {data['name']}")
    
    def test_04_update_checklist(self):
        """Test updating a checklist"""
        # First create a checklist
        checklist_data = {
            "project_id": self.project_id,
            "name": "TEST_Update Checklist Test",
            "description": "Original description"
        }
        create_response = self.session.post(f"{BASE_URL}/api/checklists", json=checklist_data)
        assert create_response.status_code == 200
        checklist_id = create_response.json()["id"]
        
        # Update it
        update_data = {
            "name": "TEST_Updated Checklist Name",
            "description": "Updated description"
        }
        response = self.session.put(f"{BASE_URL}/api/checklists/{checklist_id}", json=update_data)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["name"] == update_data["name"], "Name should be updated"
        assert data["description"] == update_data["description"], "Description should be updated"
        
        # Verify with GET
        get_response = self.session.get(f"{BASE_URL}/api/checklists/{checklist_id}")
        assert get_response.status_code == 200
        assert get_response.json()["name"] == update_data["name"], "Name should persist"
        
        print(f"Updated checklist: {data['name']}")
    
    def test_05_delete_checklist(self):
        """Test deleting a checklist"""
        # First create a checklist
        checklist_data = {
            "project_id": self.project_id,
            "name": "TEST_Delete Checklist Test",
            "description": "To be deleted"
        }
        create_response = self.session.post(f"{BASE_URL}/api/checklists", json=checklist_data)
        assert create_response.status_code == 200
        checklist_id = create_response.json()["id"]
        
        # Delete it
        response = self.session.delete(f"{BASE_URL}/api/checklists/{checklist_id}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "message" in data, "Response should contain 'message'"
        
        # Verify it's deleted
        get_response = self.session.get(f"{BASE_URL}/api/checklists/{checklist_id}")
        assert get_response.status_code == 404, "Deleted checklist should return 404"
        
        print("Checklist deleted successfully")
    
    # ============ CHECKLIST ITEM CRUD TESTS ============
    
    def test_06_add_item_to_checklist(self):
        """Test adding an item to a checklist"""
        # First create a checklist
        checklist_data = {
            "project_id": self.project_id,
            "name": "TEST_Item Test Checklist",
            "description": "For testing items"
        }
        create_response = self.session.post(f"{BASE_URL}/api/checklists", json=checklist_data)
        assert create_response.status_code == 200
        checklist_id = create_response.json()["id"]
        
        # Add an item
        item_data = {"text": "Feed the chickens"}
        response = self.session.post(f"{BASE_URL}/api/checklists/{checklist_id}/items", json=item_data)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["text"] == item_data["text"], "Item text should match"
        assert data["is_done"] == False, "New item should not be done"
        assert "id" in data, "Response should contain 'id'"
        assert data["checklist_id"] == checklist_id, "Checklist ID should match"
        
        # Store for later tests
        self.created_item_id = data["id"]
        self.test_checklist_id = checklist_id
        print(f"Added item: {data['text']} (ID: {data['id']})")
    
    def test_07_toggle_item_completion(self):
        """Test toggling item completion status"""
        # First create a checklist with an item
        checklist_data = {
            "project_id": self.project_id,
            "name": "TEST_Toggle Test Checklist",
            "description": "For testing toggle"
        }
        create_response = self.session.post(f"{BASE_URL}/api/checklists", json=checklist_data)
        assert create_response.status_code == 200
        checklist_id = create_response.json()["id"]
        
        # Add an item
        item_data = {"text": "Water the garden"}
        item_response = self.session.post(f"{BASE_URL}/api/checklists/{checklist_id}/items", json=item_data)
        assert item_response.status_code == 200
        item_id = item_response.json()["id"]
        
        # Toggle to done
        response = self.session.post(f"{BASE_URL}/api/checklist-items/{item_id}/toggle")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["is_done"] == True, "Item should be marked as done"
        
        # Toggle back to not done
        response2 = self.session.post(f"{BASE_URL}/api/checklist-items/{item_id}/toggle")
        assert response2.status_code == 200
        assert response2.json()["is_done"] == False, "Item should be marked as not done"
        
        print("Item toggle working correctly")
    
    def test_08_update_item(self):
        """Test updating a checklist item"""
        # First create a checklist with an item
        checklist_data = {
            "project_id": self.project_id,
            "name": "TEST_Update Item Checklist",
            "description": "For testing item update"
        }
        create_response = self.session.post(f"{BASE_URL}/api/checklists", json=checklist_data)
        assert create_response.status_code == 200
        checklist_id = create_response.json()["id"]
        
        # Add an item
        item_data = {"text": "Original item text"}
        item_response = self.session.post(f"{BASE_URL}/api/checklists/{checklist_id}/items", json=item_data)
        assert item_response.status_code == 200
        item_id = item_response.json()["id"]
        
        # Update the item
        update_data = {"text": "Updated item text"}
        response = self.session.put(f"{BASE_URL}/api/checklist-items/{item_id}", json=update_data)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["text"] == update_data["text"], "Item text should be updated"
        
        print(f"Updated item: {data['text']}")
    
    def test_09_delete_item(self):
        """Test deleting a checklist item"""
        # First create a checklist with an item
        checklist_data = {
            "project_id": self.project_id,
            "name": "TEST_Delete Item Checklist",
            "description": "For testing item delete"
        }
        create_response = self.session.post(f"{BASE_URL}/api/checklists", json=checklist_data)
        assert create_response.status_code == 200
        checklist_id = create_response.json()["id"]
        
        # Add an item
        item_data = {"text": "Item to delete"}
        item_response = self.session.post(f"{BASE_URL}/api/checklists/{checklist_id}/items", json=item_data)
        assert item_response.status_code == 200
        item_id = item_response.json()["id"]
        
        # Delete the item
        response = self.session.delete(f"{BASE_URL}/api/checklist-items/{item_id}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "message" in data, "Response should contain 'message'"
        
        # Verify item is deleted by checking checklist
        get_response = self.session.get(f"{BASE_URL}/api/checklists/{checklist_id}")
        assert get_response.status_code == 200
        assert len(get_response.json()["items"]) == 0, "Checklist should have no items"
        
        print("Item deleted successfully")
    
    def test_10_reset_checklist(self):
        """Test resetting all items in a checklist"""
        # First create a checklist with items
        checklist_data = {
            "project_id": self.project_id,
            "name": "TEST_Reset Checklist",
            "description": "For testing reset"
        }
        create_response = self.session.post(f"{BASE_URL}/api/checklists", json=checklist_data)
        assert create_response.status_code == 200
        checklist_id = create_response.json()["id"]
        
        # Add multiple items
        items = ["Item 1", "Item 2", "Item 3"]
        item_ids = []
        for item_text in items:
            item_response = self.session.post(
                f"{BASE_URL}/api/checklists/{checklist_id}/items", 
                json={"text": item_text}
            )
            assert item_response.status_code == 200
            item_ids.append(item_response.json()["id"])
        
        # Mark all items as done
        for item_id in item_ids:
            toggle_response = self.session.post(f"{BASE_URL}/api/checklist-items/{item_id}/toggle")
            assert toggle_response.status_code == 200
            assert toggle_response.json()["is_done"] == True
        
        # Verify all items are done
        get_response = self.session.get(f"{BASE_URL}/api/checklists/{checklist_id}")
        assert get_response.status_code == 200
        assert get_response.json()["completed_items"] == 3, "All 3 items should be completed"
        
        # Reset the checklist
        response = self.session.post(f"{BASE_URL}/api/checklists/{checklist_id}/reset")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["completed_items"] == 0, "All items should be unchecked after reset"
        assert data["total_items"] == 3, "Total items should still be 3"
        
        # Verify all items are not done
        for item in data["items"]:
            assert item["is_done"] == False, f"Item '{item['text']}' should not be done after reset"
        
        print("Checklist reset successfully")
    
    def test_11_checklist_progress_tracking(self):
        """Test that checklist progress is tracked correctly"""
        # Create a checklist
        checklist_data = {
            "project_id": self.project_id,
            "name": "TEST_Progress Checklist",
            "description": "For testing progress"
        }
        create_response = self.session.post(f"{BASE_URL}/api/checklists", json=checklist_data)
        assert create_response.status_code == 200
        checklist_id = create_response.json()["id"]
        
        # Add 4 items
        items = ["Task 1", "Task 2", "Task 3", "Task 4"]
        item_ids = []
        for item_text in items:
            item_response = self.session.post(
                f"{BASE_URL}/api/checklists/{checklist_id}/items", 
                json={"text": item_text}
            )
            assert item_response.status_code == 200
            item_ids.append(item_response.json()["id"])
        
        # Check initial progress
        get_response = self.session.get(f"{BASE_URL}/api/checklists/{checklist_id}")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["total_items"] == 4, "Should have 4 total items"
        assert data["completed_items"] == 0, "Should have 0 completed items"
        
        # Complete 2 items
        for item_id in item_ids[:2]:
            self.session.post(f"{BASE_URL}/api/checklist-items/{item_id}/toggle")
        
        # Check progress
        get_response = self.session.get(f"{BASE_URL}/api/checklists/{checklist_id}")
        data = get_response.json()
        assert data["completed_items"] == 2, "Should have 2 completed items"
        
        print(f"Progress tracking: {data['completed_items']}/{data['total_items']} items completed")
    
    def test_12_checklist_not_found(self):
        """Test 404 for non-existent checklist"""
        response = self.session.get(f"{BASE_URL}/api/checklists/non-existent-id")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("404 returned for non-existent checklist")
    
    def test_13_item_not_found(self):
        """Test 404 for non-existent item"""
        response = self.session.post(f"{BASE_URL}/api/checklist-items/non-existent-id/toggle")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("404 returned for non-existent item")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
