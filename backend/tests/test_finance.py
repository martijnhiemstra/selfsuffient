"""
Finance Module Backend Tests
Tests for: Accounts, Categories, Transactions, Recurring, Dashboard, Monthly, Runway
"""
import pytest
import requests
import os
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "admin@selfsufficient.app"
TEST_PASSWORD = "admin123"

# Test data storage
test_data = {
    "token": None,
    "project_id": None,
    "account_id": None,
    "category_id": None,
    "transaction_id": None,
    "recurring_id": None
}


class TestAuthentication:
    """Authentication tests - must run first"""
    
    def test_login_success(self):
        """Test login with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "No access_token in response"
        test_data["token"] = data["access_token"]
        print(f"Login successful, token obtained")


class TestProjectSetup:
    """Get a project ID for finance testing"""
    
    def test_get_projects(self):
        """Get list of projects to use for finance testing"""
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        response = requests.get(f"{BASE_URL}/api/projects", headers=headers)
        assert response.status_code == 200, f"Failed to get projects: {response.text}"
        data = response.json()
        assert "projects" in data, "No projects key in response"
        assert len(data["projects"]) > 0, "No projects found - need at least one project for finance testing"
        test_data["project_id"] = data["projects"][0]["id"]
        print(f"Using project ID: {test_data['project_id']}")


class TestFinanceAccounts:
    """Finance Accounts CRUD tests"""
    
    def test_create_account(self):
        """POST /api/finance/accounts - Create a new account"""
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        payload = {
            "project_id": test_data["project_id"],
            "name": "TEST_Main Bank Account",
            "type": "bank",
            "notes": "Test account for finance testing"
        }
        response = requests.post(f"{BASE_URL}/api/finance/accounts", json=payload, headers=headers)
        assert response.status_code == 200, f"Failed to create account: {response.text}"
        data = response.json()
        assert "id" in data, "No id in account response"
        assert data["name"] == "TEST_Main Bank Account"
        assert data["type"] == "bank"
        assert data["balance"] == 0.0
        test_data["account_id"] = data["id"]
        print(f"Created account: {data['id']}")
    
    def test_list_accounts(self):
        """GET /api/finance/accounts - List all accounts"""
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        response = requests.get(f"{BASE_URL}/api/finance/accounts", headers=headers)
        assert response.status_code == 200, f"Failed to list accounts: {response.text}"
        data = response.json()
        assert "accounts" in data, "No accounts key in response"
        assert "total" in data, "No total key in response"
        print(f"Found {data['total']} accounts")
    
    def test_list_accounts_by_project(self):
        """GET /api/finance/accounts?project_id=X - List accounts filtered by project"""
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        response = requests.get(
            f"{BASE_URL}/api/finance/accounts?project_id={test_data['project_id']}", 
            headers=headers
        )
        assert response.status_code == 200, f"Failed to list accounts by project: {response.text}"
        data = response.json()
        assert "accounts" in data
        # All returned accounts should belong to the project
        for acc in data["accounts"]:
            assert acc["project_id"] == test_data["project_id"]
        print(f"Found {data['total']} accounts for project")
    
    def test_get_account(self):
        """GET /api/finance/accounts/{id} - Get specific account"""
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        response = requests.get(
            f"{BASE_URL}/api/finance/accounts/{test_data['account_id']}", 
            headers=headers
        )
        assert response.status_code == 200, f"Failed to get account: {response.text}"
        data = response.json()
        assert data["id"] == test_data["account_id"]
        assert data["name"] == "TEST_Main Bank Account"
        print(f"Got account: {data['name']}")
    
    def test_update_account(self):
        """PUT /api/finance/accounts/{id} - Update account"""
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        payload = {
            "name": "TEST_Updated Bank Account",
            "notes": "Updated notes"
        }
        response = requests.put(
            f"{BASE_URL}/api/finance/accounts/{test_data['account_id']}", 
            json=payload, 
            headers=headers
        )
        assert response.status_code == 200, f"Failed to update account: {response.text}"
        data = response.json()
        assert data["name"] == "TEST_Updated Bank Account"
        print(f"Updated account name to: {data['name']}")


class TestFinanceCategories:
    """Finance Categories tests"""
    
    def test_seed_default_categories(self):
        """POST /api/finance/categories/seed/{project_id} - Seed default categories"""
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        response = requests.post(
            f"{BASE_URL}/api/finance/categories/seed/{test_data['project_id']}", 
            json={},
            headers=headers
        )
        # May return 400 if categories already exist
        if response.status_code == 400:
            print("Categories already exist for this project (expected)")
            assert "already exist" in response.json().get("detail", "").lower()
        else:
            assert response.status_code == 200, f"Failed to seed categories: {response.text}"
            data = response.json()
            assert "categories" in data
            assert data["total"] > 0
            print(f"Seeded {data['total']} default categories")
    
    def test_list_categories(self):
        """GET /api/finance/categories - List all categories"""
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        response = requests.get(f"{BASE_URL}/api/finance/categories", headers=headers)
        assert response.status_code == 200, f"Failed to list categories: {response.text}"
        data = response.json()
        assert "categories" in data
        assert "total" in data
        assert data["total"] > 0, "No categories found"
        # Store a category ID for transaction testing
        test_data["category_id"] = data["categories"][0]["id"]
        print(f"Found {data['total']} categories")
    
    def test_list_categories_by_project(self):
        """GET /api/finance/categories?project_id=X - List categories filtered by project"""
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        response = requests.get(
            f"{BASE_URL}/api/finance/categories?project_id={test_data['project_id']}", 
            headers=headers
        )
        assert response.status_code == 200, f"Failed to list categories by project: {response.text}"
        data = response.json()
        assert "categories" in data
        for cat in data["categories"]:
            assert cat["project_id"] == test_data["project_id"]
        print(f"Found {data['total']} categories for project")
    
    def test_create_custom_category(self):
        """POST /api/finance/categories - Create a custom category"""
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        payload = {
            "project_id": test_data["project_id"],
            "name": "TEST_Custom Category",
            "type": "expense"
        }
        response = requests.post(f"{BASE_URL}/api/finance/categories", json=payload, headers=headers)
        assert response.status_code == 200, f"Failed to create category: {response.text}"
        data = response.json()
        assert data["name"] == "TEST_Custom Category"
        assert data["type"] == "expense"
        print(f"Created custom category: {data['name']}")


class TestFinanceTransactions:
    """Finance Transactions CRUD tests"""
    
    def test_create_income_transaction(self):
        """POST /api/finance/transactions - Create income transaction"""
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        today = datetime.now().strftime("%Y-%m-%d")
        
        # First get an income category
        cat_response = requests.get(
            f"{BASE_URL}/api/finance/categories?project_id={test_data['project_id']}", 
            headers=headers
        )
        categories = cat_response.json()["categories"]
        income_cat = next((c for c in categories if c["type"] == "income"), categories[0])
        
        payload = {
            "date": today,
            "amount": 1000.00,  # Positive = income
            "account_id": test_data["account_id"],
            "project_id": test_data["project_id"],
            "category_id": income_cat["id"],
            "notes": "TEST_Income transaction"
        }
        response = requests.post(f"{BASE_URL}/api/finance/transactions", json=payload, headers=headers)
        assert response.status_code == 200, f"Failed to create transaction: {response.text}"
        data = response.json()
        assert "id" in data
        assert data["amount"] == 1000.00
        assert data["account_name"] is not None
        assert data["category_name"] is not None
        test_data["transaction_id"] = data["id"]
        print(f"Created income transaction: {data['id']}")
    
    def test_create_expense_transaction(self):
        """POST /api/finance/transactions - Create expense transaction"""
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Get an expense category
        cat_response = requests.get(
            f"{BASE_URL}/api/finance/categories?project_id={test_data['project_id']}", 
            headers=headers
        )
        categories = cat_response.json()["categories"]
        expense_cat = next((c for c in categories if c["type"] == "expense"), categories[0])
        
        payload = {
            "date": today,
            "amount": -250.00,  # Negative = expense
            "account_id": test_data["account_id"],
            "project_id": test_data["project_id"],
            "category_id": expense_cat["id"],
            "notes": "TEST_Expense transaction"
        }
        response = requests.post(f"{BASE_URL}/api/finance/transactions", json=payload, headers=headers)
        assert response.status_code == 200, f"Failed to create expense: {response.text}"
        data = response.json()
        assert data["amount"] == -250.00
        print(f"Created expense transaction: {data['id']}")
    
    def test_list_transactions(self):
        """GET /api/finance/transactions - List all transactions"""
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        response = requests.get(f"{BASE_URL}/api/finance/transactions", headers=headers)
        assert response.status_code == 200, f"Failed to list transactions: {response.text}"
        data = response.json()
        assert "transactions" in data
        assert "total" in data
        print(f"Found {data['total']} transactions")
    
    def test_list_transactions_by_project(self):
        """GET /api/finance/transactions?project_id=X - Filter by project"""
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        response = requests.get(
            f"{BASE_URL}/api/finance/transactions?project_id={test_data['project_id']}", 
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        for tx in data["transactions"]:
            assert tx["project_id"] == test_data["project_id"]
        print(f"Found {data['total']} transactions for project")
    
    def test_update_transaction(self):
        """PUT /api/finance/transactions/{id} - Update transaction"""
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        payload = {
            "notes": "TEST_Updated notes"
        }
        response = requests.put(
            f"{BASE_URL}/api/finance/transactions/{test_data['transaction_id']}", 
            json=payload, 
            headers=headers
        )
        assert response.status_code == 200, f"Failed to update transaction: {response.text}"
        data = response.json()
        assert data["notes"] == "TEST_Updated notes"
        print(f"Updated transaction notes")


class TestFinanceRecurring:
    """Recurring Transactions tests"""
    
    def test_create_recurring_transaction(self):
        """POST /api/finance/recurring - Create recurring transaction"""
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Get an expense category
        cat_response = requests.get(
            f"{BASE_URL}/api/finance/categories?project_id={test_data['project_id']}", 
            headers=headers
        )
        categories = cat_response.json()["categories"]
        expense_cat = next((c for c in categories if c["type"] == "expense"), categories[0])
        
        payload = {
            "name": "TEST_Monthly Rent",
            "amount": -500.00,
            "frequency": "monthly",
            "start_date": today,
            "account_id": test_data["account_id"],
            "project_id": test_data["project_id"],
            "category_id": expense_cat["id"],
            "active": True
        }
        response = requests.post(f"{BASE_URL}/api/finance/recurring", json=payload, headers=headers)
        assert response.status_code == 200, f"Failed to create recurring: {response.text}"
        data = response.json()
        assert "id" in data
        assert data["name"] == "TEST_Monthly Rent"
        assert data["frequency"] == "monthly"
        assert data["active"] == True
        test_data["recurring_id"] = data["id"]
        print(f"Created recurring transaction: {data['id']}")
    
    def test_list_recurring_transactions(self):
        """GET /api/finance/recurring - List recurring transactions"""
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        response = requests.get(f"{BASE_URL}/api/finance/recurring", headers=headers)
        assert response.status_code == 200, f"Failed to list recurring: {response.text}"
        data = response.json()
        assert "recurring_transactions" in data
        assert "total" in data
        print(f"Found {data['total']} recurring transactions")
    
    def test_list_recurring_by_project(self):
        """GET /api/finance/recurring?project_id=X - Filter by project"""
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        response = requests.get(
            f"{BASE_URL}/api/finance/recurring?project_id={test_data['project_id']}", 
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        for rec in data["recurring_transactions"]:
            assert rec["project_id"] == test_data["project_id"]
        print(f"Found {data['total']} recurring for project")
    
    def test_update_recurring_transaction(self):
        """PUT /api/finance/recurring/{id} - Update recurring"""
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        payload = {
            "name": "TEST_Updated Monthly Rent",
            "active": False
        }
        response = requests.put(
            f"{BASE_URL}/api/finance/recurring/{test_data['recurring_id']}", 
            json=payload, 
            headers=headers
        )
        assert response.status_code == 200, f"Failed to update recurring: {response.text}"
        data = response.json()
        assert data["name"] == "TEST_Updated Monthly Rent"
        assert data["active"] == False
        print(f"Updated recurring transaction")


class TestFinanceAnalytics:
    """Dashboard, Monthly Overview, and Runway tests"""
    
    def test_project_dashboard(self):
        """GET /api/finance/dashboard/{project_id} - Get project financial summary"""
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        response = requests.get(
            f"{BASE_URL}/api/finance/dashboard/{test_data['project_id']}", 
            headers=headers
        )
        assert response.status_code == 200, f"Failed to get dashboard: {response.text}"
        data = response.json()
        assert "project_id" in data
        assert "project_name" in data
        assert "total_income" in data
        assert "total_expenses" in data
        assert "total_investments" in data
        assert "net_balance" in data
        assert "avg_monthly_burn" in data
        assert "months_active" in data
        print(f"Dashboard: Income={data['total_income']}, Expenses={data['total_expenses']}, Net={data['net_balance']}")
    
    def test_monthly_overview(self):
        """GET /api/finance/monthly?month=YYYY-MM - Get monthly overview"""
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        current_month = datetime.now().strftime("%Y-%m")
        response = requests.get(
            f"{BASE_URL}/api/finance/monthly?month={current_month}", 
            headers=headers
        )
        assert response.status_code == 200, f"Failed to get monthly: {response.text}"
        data = response.json()
        assert "month" in data
        assert data["month"] == current_month
        assert "total_income" in data
        assert "total_expenses" in data
        assert "total_investments" in data
        assert "net_result" in data
        assert "by_project" in data
        assert "by_category" in data
        print(f"Monthly {current_month}: Income={data['total_income']}, Expenses={data['total_expenses']}, Net={data['net_result']}")
    
    def test_monthly_overview_by_project(self):
        """GET /api/finance/monthly?month=YYYY-MM&project_id=X - Monthly filtered by project"""
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        current_month = datetime.now().strftime("%Y-%m")
        response = requests.get(
            f"{BASE_URL}/api/finance/monthly?month={current_month}&project_id={test_data['project_id']}", 
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["month"] == current_month
        print(f"Monthly for project: Net={data['net_result']}")
    
    def test_monthly_invalid_format(self):
        """GET /api/finance/monthly?month=invalid - Should return 400"""
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        response = requests.get(
            f"{BASE_URL}/api/finance/monthly?month=invalid", 
            headers=headers
        )
        assert response.status_code == 400, f"Expected 400 for invalid month format"
        print("Invalid month format correctly rejected")
    
    def test_runway_calculation(self):
        """GET /api/finance/runway - Calculate financial runway"""
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        response = requests.get(f"{BASE_URL}/api/finance/runway", headers=headers)
        assert response.status_code == 200, f"Failed to get runway: {response.text}"
        data = response.json()
        assert "total_liquid_cash" in data
        assert "avg_monthly_burn" in data
        assert "runway_months" in data
        assert "safety_threshold" in data
        assert "is_below_threshold" in data
        assert "accounts_included" in data
        print(f"Runway: Cash={data['total_liquid_cash']}, Burn={data['avg_monthly_burn']}, Months={data['runway_months']}")
    
    def test_runway_with_custom_threshold(self):
        """GET /api/finance/runway?safety_threshold=5000 - Custom threshold"""
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        response = requests.get(
            f"{BASE_URL}/api/finance/runway?safety_threshold=5000", 
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["safety_threshold"] == 5000.0
        print(f"Runway with custom threshold: Below threshold={data['is_below_threshold']}")


class TestFinanceCleanup:
    """Cleanup test data"""
    
    def test_delete_recurring(self):
        """DELETE /api/finance/recurring/{id} - Delete recurring transaction"""
        if not test_data.get("recurring_id"):
            pytest.skip("No recurring transaction to delete")
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        response = requests.delete(
            f"{BASE_URL}/api/finance/recurring/{test_data['recurring_id']}", 
            headers=headers
        )
        assert response.status_code == 200, f"Failed to delete recurring: {response.text}"
        print("Deleted recurring transaction")
    
    def test_delete_transaction(self):
        """DELETE /api/finance/transactions/{id} - Delete transaction"""
        if not test_data.get("transaction_id"):
            pytest.skip("No transaction to delete")
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        response = requests.delete(
            f"{BASE_URL}/api/finance/transactions/{test_data['transaction_id']}", 
            headers=headers
        )
        assert response.status_code == 200, f"Failed to delete transaction: {response.text}"
        print("Deleted transaction")
    
    def test_delete_account_with_transactions_fails(self):
        """DELETE /api/finance/accounts/{id} - Should fail if transactions exist"""
        # First create a transaction for the account
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        today = datetime.now().strftime("%Y-%m-%d")
        
        cat_response = requests.get(
            f"{BASE_URL}/api/finance/categories?project_id={test_data['project_id']}", 
            headers=headers
        )
        categories = cat_response.json()["categories"]
        
        # Create a transaction
        tx_payload = {
            "date": today,
            "amount": 100.00,
            "account_id": test_data["account_id"],
            "project_id": test_data["project_id"],
            "category_id": categories[0]["id"],
            "notes": "TEST_Temp transaction"
        }
        tx_response = requests.post(f"{BASE_URL}/api/finance/transactions", json=tx_payload, headers=headers)
        
        # Try to delete account - should fail
        response = requests.delete(
            f"{BASE_URL}/api/finance/accounts/{test_data['account_id']}", 
            headers=headers
        )
        assert response.status_code == 400, f"Expected 400 when deleting account with transactions"
        assert "transactions" in response.json().get("detail", "").lower()
        print("Account deletion correctly blocked due to existing transactions")
        
        # Clean up the transaction
        if tx_response.status_code == 200:
            tx_id = tx_response.json()["id"]
            requests.delete(f"{BASE_URL}/api/finance/transactions/{tx_id}", headers=headers)
    
    def test_delete_account(self):
        """DELETE /api/finance/accounts/{id} - Delete account after cleaning transactions"""
        if not test_data.get("account_id"):
            pytest.skip("No account to delete")
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        
        # First delete all transactions for this account
        tx_response = requests.get(
            f"{BASE_URL}/api/finance/transactions?account_id={test_data['account_id']}", 
            headers=headers
        )
        if tx_response.status_code == 200:
            for tx in tx_response.json().get("transactions", []):
                requests.delete(f"{BASE_URL}/api/finance/transactions/{tx['id']}", headers=headers)
        
        # Now delete the account
        response = requests.delete(
            f"{BASE_URL}/api/finance/accounts/{test_data['account_id']}", 
            headers=headers
        )
        assert response.status_code == 200, f"Failed to delete account: {response.text}"
        print("Deleted account")


class TestFinanceErrorHandling:
    """Error handling tests"""
    
    def test_create_account_invalid_project(self):
        """POST /api/finance/accounts - Invalid project ID"""
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        payload = {
            "project_id": "invalid-project-id",
            "name": "Test Account",
            "type": "bank"
        }
        response = requests.post(f"{BASE_URL}/api/finance/accounts", json=payload, headers=headers)
        assert response.status_code == 404, f"Expected 404 for invalid project"
        print("Invalid project correctly rejected")
    
    def test_create_transaction_invalid_account(self):
        """POST /api/finance/transactions - Invalid account ID"""
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Get a valid category
        cat_response = requests.get(
            f"{BASE_URL}/api/finance/categories?project_id={test_data['project_id']}", 
            headers=headers
        )
        categories = cat_response.json()["categories"]
        
        payload = {
            "date": today,
            "amount": 100.00,
            "account_id": "invalid-account-id",
            "project_id": test_data["project_id"],
            "category_id": categories[0]["id"] if categories else "invalid",
            "notes": "Test"
        }
        response = requests.post(f"{BASE_URL}/api/finance/transactions", json=payload, headers=headers)
        assert response.status_code == 404, f"Expected 404 for invalid account"
        print("Invalid account correctly rejected")
    
    def test_get_nonexistent_account(self):
        """GET /api/finance/accounts/{id} - Non-existent account"""
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        response = requests.get(
            f"{BASE_URL}/api/finance/accounts/nonexistent-id", 
            headers=headers
        )
        assert response.status_code == 404
        print("Non-existent account correctly returns 404")
    
    def test_unauthorized_access(self):
        """Test endpoints without auth token"""
        response = requests.get(f"{BASE_URL}/api/finance/accounts")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth"
        print("Unauthorized access correctly rejected")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
