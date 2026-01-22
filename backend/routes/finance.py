"""Finance routes - Accounts, Categories, Transactions, Analytics."""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
import uuid

from config import db
from models import (
    AccountCreate, AccountUpdate, AccountResponse, AccountListResponse,
    CategoryCreate, CategoryUpdate, CategoryResponse, CategoryListResponse,
    TransactionCreate, TransactionUpdate, TransactionResponse, TransactionListResponse,
    RecurringTransactionCreate, RecurringTransactionUpdate, RecurringTransactionResponse, RecurringTransactionListResponse,
    SavingsGoalCreate, SavingsGoalUpdate, SavingsGoalResponse, SavingsGoalListResponse,
    ProjectFinanceSummary, MonthlyOverview, RunwayCalculation, DEFAULT_CATEGORIES, MessageResponse
)
from services import get_current_user

router = APIRouter()


# ============ ACCOUNTS ============

@router.post("/accounts", response_model=AccountResponse)
async def create_account(data: AccountCreate, current_user: dict = Depends(get_current_user)):
    """Create a new financial account for a project"""
    # Verify project access
    project = await db.projects.find_one({"id": data.project_id, "user_id": current_user["id"]})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    account_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    account_doc = {
        "id": account_id,
        "user_id": current_user["id"],
        "project_id": data.project_id,
        "name": data.name,
        "type": data.type.value,
        "starting_balance": data.starting_balance,
        "notes": data.notes,
        "created_at": now,
        "updated_at": now
    }
    
    await db.finance_accounts.insert_one(account_doc)
    
    return AccountResponse(**{k: v for k, v in account_doc.items() if k != "_id"}, balance=data.starting_balance)


@router.get("/accounts", response_model=AccountListResponse)
async def list_accounts(
    project_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """List all accounts, optionally filtered by project"""
    query = {"user_id": current_user["id"]}
    if project_id:
        query["project_id"] = project_id
    
    accounts = await db.finance_accounts.find(query, {"_id": 0}).to_list(1000)
    
    # Calculate balance for each account
    result = []
    for acc in accounts:
        balance = await calculate_account_balance(acc["id"])
        result.append(AccountResponse(**acc, balance=balance))
    
    return AccountListResponse(accounts=result, total=len(result))


@router.get("/accounts/{account_id}", response_model=AccountResponse)
async def get_account(account_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific account"""
    account = await db.finance_accounts.find_one(
        {"id": account_id, "user_id": current_user["id"]}, {"_id": 0}
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    balance = await calculate_account_balance(account_id)
    return AccountResponse(**account, balance=balance)


@router.put("/accounts/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: str, data: AccountUpdate, current_user: dict = Depends(get_current_user)
):
    """Update an account"""
    account = await db.finance_accounts.find_one({"id": account_id, "user_id": current_user["id"]})
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    update_data = {k: v.value if hasattr(v, 'value') else v for k, v in data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.finance_accounts.update_one({"id": account_id}, {"$set": update_data})
    updated = await db.finance_accounts.find_one({"id": account_id}, {"_id": 0})
    balance = await calculate_account_balance(account_id)
    return AccountResponse(**updated, balance=balance)


@router.delete("/accounts/{account_id}", response_model=MessageResponse)
async def delete_account(account_id: str, current_user: dict = Depends(get_current_user)):
    """Delete an account (only if no transactions)"""
    account = await db.finance_accounts.find_one({"id": account_id, "user_id": current_user["id"]})
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Check for transactions
    tx_count = await db.finance_transactions.count_documents({"account_id": account_id})
    if tx_count > 0:
        raise HTTPException(status_code=400, detail=f"Cannot delete account with {tx_count} transactions")
    
    await db.finance_accounts.delete_one({"id": account_id})
    return MessageResponse(message="Account deleted")


# ============ CATEGORIES ============

@router.post("/categories", response_model=CategoryResponse)
async def create_category(data: CategoryCreate, current_user: dict = Depends(get_current_user)):
    """Create a new category for a project"""
    project = await db.projects.find_one({"id": data.project_id, "user_id": current_user["id"]})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    category_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    category_doc = {
        "id": category_id,
        "user_id": current_user["id"],
        "project_id": data.project_id,
        "name": data.name,
        "type": data.type.value,
        "created_at": now
    }
    
    await db.finance_categories.insert_one(category_doc)
    return CategoryResponse(**{k: v for k, v in category_doc.items() if k != "_id"})


@router.get("/categories", response_model=CategoryListResponse)
async def list_categories(
    project_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """List all categories, optionally filtered by project"""
    query = {"user_id": current_user["id"]}
    if project_id:
        query["project_id"] = project_id
    
    categories = await db.finance_categories.find(query, {"_id": 0}).to_list(1000)
    return CategoryListResponse(
        categories=[CategoryResponse(**c) for c in categories],
        total=len(categories)
    )


@router.post("/categories/seed/{project_id}", response_model=CategoryListResponse)
async def seed_default_categories(project_id: str, current_user: dict = Depends(get_current_user)):
    """Seed default categories for a project"""
    project = await db.projects.find_one({"id": project_id, "user_id": current_user["id"]})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if categories already exist
    existing = await db.finance_categories.count_documents({"project_id": project_id, "user_id": current_user["id"]})
    if existing > 0:
        raise HTTPException(status_code=400, detail="Categories already exist for this project")
    
    now = datetime.now(timezone.utc).isoformat()
    categories = []
    
    for cat in DEFAULT_CATEGORIES:
        category_doc = {
            "id": str(uuid.uuid4()),
            "user_id": current_user["id"],
            "project_id": project_id,
            "name": cat["name"],
            "type": cat["type"],
            "created_at": now
        }
        await db.finance_categories.insert_one(category_doc)
        categories.append(CategoryResponse(**{k: v for k, v in category_doc.items() if k != "_id"}))
    
    return CategoryListResponse(categories=categories, total=len(categories))


@router.delete("/categories/{category_id}", response_model=MessageResponse)
async def delete_category(category_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a category (only if no transactions)"""
    category = await db.finance_categories.find_one({"id": category_id, "user_id": current_user["id"]})
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    tx_count = await db.finance_transactions.count_documents({"category_id": category_id})
    if tx_count > 0:
        raise HTTPException(status_code=400, detail=f"Cannot delete category with {tx_count} transactions")
    
    await db.finance_categories.delete_one({"id": category_id})
    return MessageResponse(message="Category deleted")


# ============ TRANSACTIONS ============

@router.post("/transactions", response_model=TransactionResponse)
async def create_transaction(data: TransactionCreate, current_user: dict = Depends(get_current_user)):
    """Create a new transaction"""
    # Verify project access
    project = await db.projects.find_one({"id": data.project_id, "user_id": current_user["id"]})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Verify account
    account = await db.finance_accounts.find_one({"id": data.account_id, "user_id": current_user["id"]})
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Verify category
    category = await db.finance_categories.find_one({"id": data.category_id, "user_id": current_user["id"]})
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Verify savings goal if provided
    savings_goal = None
    if data.savings_goal_id:
        savings_goal = await db.finance_savings_goals.find_one({"id": data.savings_goal_id, "user_id": current_user["id"]})
        if not savings_goal:
            raise HTTPException(status_code=404, detail="Savings goal not found")
    
    tx_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    tx_doc = {
        "id": tx_id,
        "user_id": current_user["id"],
        "date": data.date,
        "amount": data.amount,
        "account_id": data.account_id,
        "project_id": data.project_id,
        "category_id": data.category_id,
        "notes": data.notes,
        "linked_transaction_id": data.linked_transaction_id,
        "savings_goal_id": data.savings_goal_id,
        "created_at": now,
        "updated_at": now
    }
    
    await db.finance_transactions.insert_one(tx_doc)
    
    return TransactionResponse(
        **{k: v for k, v in tx_doc.items() if k != "_id"},
        account_name=account["name"],
        project_name=project["name"],
        category_name=category["name"],
        category_type=category["type"],
        savings_goal_name=savings_goal["name"] if savings_goal else None
    )


@router.get("/transactions", response_model=TransactionListResponse)
async def list_transactions(
    project_id: Optional[str] = None,
    account_id: Optional[str] = None,
    category_id: Optional[str] = None,
    savings_goal_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sort_by: str = "date",
    sort_order: str = "desc",
    limit: int = Query(100, le=1000),
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """List transactions with filters"""
    query = {"user_id": current_user["id"]}
    
    if project_id:
        query["project_id"] = project_id
    if account_id:
        query["account_id"] = account_id
    if category_id:
        query["category_id"] = category_id
    if savings_goal_id:
        query["savings_goal_id"] = savings_goal_id
    if start_date:
        query["date"] = {"$gte": start_date}
    if end_date:
        if "date" in query:
            query["date"]["$lte"] = end_date
        else:
            query["date"] = {"$lte": end_date}
    
    sort_direction = -1 if sort_order == "desc" else 1
    total = await db.finance_transactions.count_documents(query)
    
    transactions = await db.finance_transactions.find(query, {"_id": 0}) \
        .sort(sort_by, sort_direction) \
        .skip(offset) \
        .limit(limit) \
        .to_list(limit)
    
    # Enrich with names
    result = []
    for tx in transactions:
        account = await db.finance_accounts.find_one({"id": tx["account_id"]}, {"_id": 0, "name": 1})
        project = await db.projects.find_one({"id": tx["project_id"]}, {"_id": 0, "name": 1})
        category = await db.finance_categories.find_one({"id": tx["category_id"]}, {"_id": 0, "name": 1, "type": 1})
        savings_goal = None
        if tx.get("savings_goal_id"):
            savings_goal = await db.finance_savings_goals.find_one({"id": tx["savings_goal_id"]}, {"_id": 0, "name": 1})
        
        result.append(TransactionResponse(
            **tx,
            account_name=account["name"] if account else None,
            project_name=project["name"] if project else None,
            category_name=category["name"] if category else None,
            category_type=category["type"] if category else None,
            savings_goal_name=savings_goal["name"] if savings_goal else None
        ))
    
    return TransactionListResponse(transactions=result, total=total)


@router.put("/transactions/{tx_id}", response_model=TransactionResponse)
async def update_transaction(
    tx_id: str, data: TransactionUpdate, current_user: dict = Depends(get_current_user)
):
    """Update a transaction"""
    tx = await db.finance_transactions.find_one({"id": tx_id, "user_id": current_user["id"]})
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Validate savings_goal_id if provided
    if data.savings_goal_id is not None and data.savings_goal_id != "":
        savings_goal_check = await db.finance_savings_goals.find_one({"id": data.savings_goal_id, "user_id": current_user["id"]})
        if not savings_goal_check:
            raise HTTPException(status_code=404, detail="Savings goal not found")
    
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    # Allow clearing savings_goal_id by setting it to empty string or null
    if data.savings_goal_id == "":
        update_data["savings_goal_id"] = None
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.finance_transactions.update_one({"id": tx_id}, {"$set": update_data})
    updated = await db.finance_transactions.find_one({"id": tx_id}, {"_id": 0})
    
    account = await db.finance_accounts.find_one({"id": updated["account_id"]}, {"_id": 0, "name": 1})
    project = await db.projects.find_one({"id": updated["project_id"]}, {"_id": 0, "name": 1})
    category = await db.finance_categories.find_one({"id": updated["category_id"]}, {"_id": 0, "name": 1, "type": 1})
    savings_goal = None
    if updated.get("savings_goal_id"):
        savings_goal = await db.finance_savings_goals.find_one({"id": updated["savings_goal_id"]}, {"_id": 0, "name": 1})
    
    return TransactionResponse(
        **updated,
        account_name=account["name"] if account else None,
        project_name=project["name"] if project else None,
        category_name=category["name"] if category else None,
        category_type=category["type"] if category else None,
        savings_goal_name=savings_goal["name"] if savings_goal else None
    )


@router.delete("/transactions/{tx_id}", response_model=MessageResponse)
async def delete_transaction(tx_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a transaction"""
    tx = await db.finance_transactions.find_one({"id": tx_id, "user_id": current_user["id"]})
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    await db.finance_transactions.delete_one({"id": tx_id})
    return MessageResponse(message="Transaction deleted")


# ============ RECURRING TRANSACTIONS ============

@router.post("/recurring", response_model=RecurringTransactionResponse)
async def create_recurring_transaction(
    data: RecurringTransactionCreate, current_user: dict = Depends(get_current_user)
):
    """Create a recurring transaction template"""
    project = await db.projects.find_one({"id": data.project_id, "user_id": current_user["id"]})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    account = await db.finance_accounts.find_one({"id": data.account_id, "user_id": current_user["id"]})
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    category = await db.finance_categories.find_one({"id": data.category_id, "user_id": current_user["id"]})
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    rec_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    rec_doc = {
        "id": rec_id,
        "user_id": current_user["id"],
        "name": data.name,
        "amount": data.amount,
        "frequency": data.frequency.value,
        "start_date": data.start_date,
        "next_execution_date": data.start_date,
        "account_id": data.account_id,
        "project_id": data.project_id,
        "category_id": data.category_id,
        "active": data.active,
        "created_at": now,
        "updated_at": now
    }
    
    await db.finance_recurring.insert_one(rec_doc)
    
    return RecurringTransactionResponse(
        **{k: v for k, v in rec_doc.items() if k != "_id"},
        account_name=account["name"],
        project_name=project["name"],
        category_name=category["name"]
    )


@router.get("/recurring", response_model=RecurringTransactionListResponse)
async def list_recurring_transactions(
    project_id: Optional[str] = None,
    active_only: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """List recurring transactions"""
    query = {"user_id": current_user["id"]}
    if project_id:
        query["project_id"] = project_id
    if active_only:
        query["active"] = True
    
    recurring = await db.finance_recurring.find(query, {"_id": 0}).to_list(1000)
    
    result = []
    for rec in recurring:
        account = await db.finance_accounts.find_one({"id": rec["account_id"]}, {"_id": 0, "name": 1})
        project = await db.projects.find_one({"id": rec["project_id"]}, {"_id": 0, "name": 1})
        category = await db.finance_categories.find_one({"id": rec["category_id"]}, {"_id": 0, "name": 1})
        
        result.append(RecurringTransactionResponse(
            **rec,
            account_name=account["name"] if account else None,
            project_name=project["name"] if project else None,
            category_name=category["name"] if category else None
        ))
    
    return RecurringTransactionListResponse(recurring_transactions=result, total=len(result))


@router.put("/recurring/{rec_id}", response_model=RecurringTransactionResponse)
async def update_recurring_transaction(
    rec_id: str, data: RecurringTransactionUpdate, current_user: dict = Depends(get_current_user)
):
    """Update a recurring transaction"""
    rec = await db.finance_recurring.find_one({"id": rec_id, "user_id": current_user["id"]})
    if not rec:
        raise HTTPException(status_code=404, detail="Recurring transaction not found")
    
    update_data = {k: v.value if hasattr(v, 'value') else v for k, v in data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.finance_recurring.update_one({"id": rec_id}, {"$set": update_data})
    updated = await db.finance_recurring.find_one({"id": rec_id}, {"_id": 0})
    
    account = await db.finance_accounts.find_one({"id": updated["account_id"]}, {"_id": 0, "name": 1})
    project = await db.projects.find_one({"id": updated["project_id"]}, {"_id": 0, "name": 1})
    category = await db.finance_categories.find_one({"id": updated["category_id"]}, {"_id": 0, "name": 1})
    
    return RecurringTransactionResponse(
        **updated,
        account_name=account["name"] if account else None,
        project_name=project["name"] if project else None,
        category_name=category["name"] if category else None
    )


@router.delete("/recurring/{rec_id}", response_model=MessageResponse)
async def delete_recurring_transaction(rec_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a recurring transaction"""
    rec = await db.finance_recurring.find_one({"id": rec_id, "user_id": current_user["id"]})
    if not rec:
        raise HTTPException(status_code=404, detail="Recurring transaction not found")
    
    await db.finance_recurring.delete_one({"id": rec_id})
    return MessageResponse(message="Recurring transaction deleted")


# ============ ANALYTICS ============

async def calculate_account_balance(account_id: str, starting_balance: float = 0.0) -> float:
    """Calculate current balance of an account (starting_balance + sum of transactions)"""
    pipeline = [
        {"$match": {"account_id": account_id}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ]
    result = await db.finance_transactions.aggregate(pipeline).to_list(1)
    transaction_sum = result[0]["total"] if result else 0.0
    return starting_balance + transaction_sum


@router.get("/dashboard/{project_id}", response_model=ProjectFinanceSummary)
async def get_project_finance_dashboard(project_id: str, current_user: dict = Depends(get_current_user)):
    """Get financial summary for a project"""
    project = await db.projects.find_one({"id": project_id, "user_id": current_user["id"]}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get all categories for this project to identify types
    categories = await db.finance_categories.find({"project_id": project_id}, {"_id": 0}).to_list(1000)
    cat_types = {c["id"]: c["type"] for c in categories}
    
    # Get all transactions for this project
    transactions = await db.finance_transactions.find({"project_id": project_id}, {"_id": 0}).to_list(10000)
    
    total_income = 0.0
    total_expenses = 0.0
    total_investments = 0.0
    
    for tx in transactions:
        cat_type = cat_types.get(tx["category_id"], "expense")
        if cat_type == "income" or tx["amount"] > 0:
            total_income += abs(tx["amount"])
        elif cat_type == "investment":
            total_investments += abs(tx["amount"])
        else:
            total_expenses += abs(tx["amount"])
    
    # Calculate months active
    start_date = datetime.fromisoformat(project["created_at"].replace("Z", "+00:00"))
    months_active = max(1, (datetime.now(timezone.utc) - start_date).days // 30)
    
    # Average monthly burn (expenses only, not investments)
    avg_monthly_burn = total_expenses / months_active if months_active > 0 else 0.0
    
    return ProjectFinanceSummary(
        project_id=project_id,
        project_name=project["name"],
        total_income=round(total_income, 2),
        total_expenses=round(total_expenses, 2),
        total_investments=round(total_investments, 2),
        net_balance=round(total_income - total_expenses - total_investments, 2),
        avg_monthly_burn=round(avg_monthly_burn, 2),
        months_active=months_active
    )


@router.get("/monthly", response_model=MonthlyOverview)
async def get_monthly_overview(
    month: str = Query(..., description="Month in YYYY-MM format"),
    project_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get monthly financial overview"""
    # Validate month format
    try:
        year, mon = map(int, month.split("-"))
        start_date = f"{month}-01"
        # Calculate end of month
        next_month = datetime(year, mon, 1) + relativedelta(months=1)
        end_date = (next_month - relativedelta(days=1)).strftime("%Y-%m-%d")
    except:
        raise HTTPException(status_code=400, detail="Invalid month format. Use YYYY-MM")
    
    query = {
        "user_id": current_user["id"],
        "date": {"$gte": start_date, "$lte": end_date}
    }
    if project_id:
        query["project_id"] = project_id
    
    transactions = await db.finance_transactions.find(query, {"_id": 0}).to_list(10000)
    
    # Get categories for type lookup
    cat_ids = list(set(tx["category_id"] for tx in transactions))
    categories = await db.finance_categories.find({"id": {"$in": cat_ids}}, {"_id": 0}).to_list(1000)
    cat_map = {c["id"]: c for c in categories}
    
    # Get projects for name lookup
    proj_ids = list(set(tx["project_id"] for tx in transactions))
    projects = await db.projects.find({"id": {"$in": proj_ids}}, {"_id": 0, "id": 1, "name": 1}).to_list(1000)
    proj_map = {p["id"]: p["name"] for p in projects}
    
    total_income = 0.0
    total_expenses = 0.0
    total_investments = 0.0
    by_project = {}
    by_category = {}
    
    for tx in transactions:
        cat = cat_map.get(tx["category_id"], {})
        cat_type = cat.get("type", "expense")
        cat_name = cat.get("name", "Unknown")
        proj_name = proj_map.get(tx["project_id"], "Unknown")
        
        amount = tx["amount"]
        
        if cat_type == "income" or amount > 0:
            total_income += abs(amount)
        elif cat_type == "investment":
            total_investments += abs(amount)
        else:
            total_expenses += abs(amount)
        
        # By project
        if proj_name not in by_project:
            by_project[proj_name] = {"income": 0, "expenses": 0, "investments": 0}
        if cat_type == "income" or amount > 0:
            by_project[proj_name]["income"] += abs(amount)
        elif cat_type == "investment":
            by_project[proj_name]["investments"] += abs(amount)
        else:
            by_project[proj_name]["expenses"] += abs(amount)
        
        # By category
        if cat_name not in by_category:
            by_category[cat_name] = {"type": cat_type, "total": 0}
        by_category[cat_name]["total"] += abs(amount)
    
    return MonthlyOverview(
        month=month,
        total_income=round(total_income, 2),
        total_expenses=round(total_expenses, 2),
        total_investments=round(total_investments, 2),
        net_result=round(total_income - total_expenses - total_investments, 2),
        by_project=[{"name": k, **v} for k, v in by_project.items()],
        by_category=[{"name": k, **v} for k, v in by_category.items()]
    )


@router.get("/runway", response_model=RunwayCalculation)
async def calculate_runway(
    account_ids: Optional[str] = Query(None, description="Comma-separated account IDs to include"),
    safety_threshold: float = Query(1000.0, description="Minimum cash safety threshold"),
    months_for_average: int = Query(6, description="Number of months to calculate average burn"),
    current_user: dict = Depends(get_current_user)
):
    """Calculate financial runway based on liquid cash and burn rate"""
    
    # Get accounts to include (only bank and cash by default)
    if account_ids:
        acc_ids = [a.strip() for a in account_ids.split(",")]
        accounts = await db.finance_accounts.find(
            {"id": {"$in": acc_ids}, "user_id": current_user["id"]},
            {"_id": 0}
        ).to_list(100)
    else:
        # Default: only bank and cash accounts
        accounts = await db.finance_accounts.find(
            {"user_id": current_user["id"], "type": {"$in": ["bank", "cash"]}},
            {"_id": 0}
        ).to_list(100)
    
    # Calculate total liquid cash
    accounts_included = []
    total_liquid_cash = 0.0
    
    for acc in accounts:
        balance = await calculate_account_balance(acc["id"])
        total_liquid_cash += balance
        accounts_included.append({
            "id": acc["id"],
            "name": acc["name"],
            "type": acc["type"],
            "balance": round(balance, 2)
        })
    
    # Calculate average monthly burn over the past N months
    end_date = datetime.now(timezone.utc)
    start_date = end_date - relativedelta(months=months_for_average)
    
    # Get expense categories (exclude income and investment)
    expense_categories = await db.finance_categories.find(
        {"user_id": current_user["id"], "type": "expense"},
        {"_id": 0, "id": 1}
    ).to_list(1000)
    expense_cat_ids = [c["id"] for c in expense_categories]
    
    # Get expense transactions
    expenses = await db.finance_transactions.find({
        "user_id": current_user["id"],
        "category_id": {"$in": expense_cat_ids},
        "date": {"$gte": start_date.strftime("%Y-%m-%d"), "$lte": end_date.strftime("%Y-%m-%d")}
    }, {"_id": 0, "amount": 1}).to_list(10000)
    
    total_expenses = sum(abs(tx["amount"]) for tx in expenses)
    avg_monthly_burn = total_expenses / months_for_average if months_for_average > 0 else 0.0
    
    # Calculate runway
    runway_months = total_liquid_cash / avg_monthly_burn if avg_monthly_burn > 0 else float('inf')
    if runway_months == float('inf'):
        runway_months = 999.0  # Cap for JSON serialization
    
    return RunwayCalculation(
        total_liquid_cash=round(total_liquid_cash, 2),
        avg_monthly_burn=round(avg_monthly_burn, 2),
        runway_months=round(runway_months, 1),
        safety_threshold=safety_threshold,
        is_below_threshold=total_liquid_cash < safety_threshold,
        accounts_included=accounts_included
    )


# ============ SAVINGS GOALS ============

async def calculate_savings_goal_progress(goal_id: str) -> tuple:
    """Calculate current amount saved towards a goal"""
    pipeline = [
        {"$match": {"savings_goal_id": goal_id}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ]
    result = await db.finance_transactions.aggregate(pipeline).to_list(1)
    current = abs(result[0]["total"]) if result else 0.0
    return current


@router.post("/savings-goals", response_model=SavingsGoalResponse)
async def create_savings_goal(data: SavingsGoalCreate, current_user: dict = Depends(get_current_user)):
    """Create a new savings goal"""
    project = await db.projects.find_one({"id": data.project_id, "user_id": current_user["id"]})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    goal_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    goal_doc = {
        "id": goal_id,
        "user_id": current_user["id"],
        "project_id": data.project_id,
        "name": data.name,
        "description": data.description,
        "target_amount": data.target_amount,
        "created_at": now,
        "updated_at": now
    }
    
    await db.finance_savings_goals.insert_one(goal_doc)
    
    return SavingsGoalResponse(
        **{k: v for k, v in goal_doc.items() if k != "_id"},
        project_name=project["name"],
        current_amount=0.0,
        progress_percent=0.0
    )


@router.get("/savings-goals", response_model=SavingsGoalListResponse)
async def list_savings_goals(
    project_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """List all savings goals"""
    query = {"user_id": current_user["id"]}
    if project_id:
        query["project_id"] = project_id
    
    goals = await db.finance_savings_goals.find(query, {"_id": 0}).to_list(1000)
    
    result = []
    for goal in goals:
        project = await db.projects.find_one({"id": goal["project_id"]}, {"_id": 0, "name": 1})
        current_amount = await calculate_savings_goal_progress(goal["id"])
        progress = (current_amount / goal["target_amount"] * 100) if goal["target_amount"] > 0 else 0
        
        result.append(SavingsGoalResponse(
            **goal,
            project_name=project["name"] if project else None,
            current_amount=round(current_amount, 2),
            progress_percent=round(min(progress, 100), 1)
        ))
    
    return SavingsGoalListResponse(savings_goals=result, total=len(result))


@router.get("/savings-goals/{goal_id}", response_model=SavingsGoalResponse)
async def get_savings_goal(goal_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific savings goal"""
    goal = await db.finance_savings_goals.find_one({"id": goal_id, "user_id": current_user["id"]}, {"_id": 0})
    if not goal:
        raise HTTPException(status_code=404, detail="Savings goal not found")
    
    project = await db.projects.find_one({"id": goal["project_id"]}, {"_id": 0, "name": 1})
    current_amount = await calculate_savings_goal_progress(goal_id)
    progress = (current_amount / goal["target_amount"] * 100) if goal["target_amount"] > 0 else 0
    
    return SavingsGoalResponse(
        **goal,
        project_name=project["name"] if project else None,
        current_amount=round(current_amount, 2),
        progress_percent=round(min(progress, 100), 1)
    )


@router.put("/savings-goals/{goal_id}", response_model=SavingsGoalResponse)
async def update_savings_goal(
    goal_id: str, data: SavingsGoalUpdate, current_user: dict = Depends(get_current_user)
):
    """Update a savings goal"""
    goal = await db.finance_savings_goals.find_one({"id": goal_id, "user_id": current_user["id"]})
    if not goal:
        raise HTTPException(status_code=404, detail="Savings goal not found")
    
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.finance_savings_goals.update_one({"id": goal_id}, {"$set": update_data})
    updated = await db.finance_savings_goals.find_one({"id": goal_id}, {"_id": 0})
    
    project = await db.projects.find_one({"id": updated["project_id"]}, {"_id": 0, "name": 1})
    current_amount = await calculate_savings_goal_progress(goal_id)
    progress = (current_amount / updated["target_amount"] * 100) if updated["target_amount"] > 0 else 0
    
    return SavingsGoalResponse(
        **updated,
        project_name=project["name"] if project else None,
        current_amount=round(current_amount, 2),
        progress_percent=round(min(progress, 100), 1)
    )


@router.delete("/savings-goals/{goal_id}", response_model=MessageResponse)
async def delete_savings_goal(goal_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a savings goal (unlinks all transactions)"""
    goal = await db.finance_savings_goals.find_one({"id": goal_id, "user_id": current_user["id"]})
    if not goal:
        raise HTTPException(status_code=404, detail="Savings goal not found")
    
    # Unlink all transactions from this goal
    await db.finance_transactions.update_many(
        {"savings_goal_id": goal_id},
        {"$set": {"savings_goal_id": None}}
    )
    
    await db.finance_savings_goals.delete_one({"id": goal_id})
    return MessageResponse(message="Savings goal deleted")
