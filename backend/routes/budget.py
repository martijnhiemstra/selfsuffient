"""Budget routes - Expense Periods and Expected Items."""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
import uuid

from config import db
from models import (
    ExpensePeriodCreate, ExpensePeriodUpdate, ExpensePeriodResponse, ExpensePeriodListResponse,
    ExpectedItemCreate, ExpectedItemUpdate, ExpectedItemResponse, ExpectedItemListResponse,
    MonthlyBudgetItem, MonthlyBudgetComparison, MessageResponse
)
from services import get_current_user

router = APIRouter()


# ============ EXPENSE PERIODS ============

@router.post("/periods", response_model=ExpensePeriodResponse)
async def create_expense_period(data: ExpensePeriodCreate, current_user: dict = Depends(get_current_user)):
    """Create a new expense period"""
    project = await db.projects.find_one({"id": data.project_id, "user_id": current_user["id"]})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Validate month format
    try:
        datetime.strptime(data.start_month, "%Y-%m")
        datetime.strptime(data.end_month, "%Y-%m")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid month format. Use YYYY-MM")
    
    if data.start_month > data.end_month:
        raise HTTPException(status_code=400, detail="Start month must be before end month")
    
    period_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    period_doc = {
        "id": period_id,
        "user_id": current_user["id"],
        "project_id": data.project_id,
        "name": data.name,
        "start_month": data.start_month,
        "end_month": data.end_month,
        "notes": data.notes,
        "created_at": now,
        "updated_at": now
    }
    
    await db.expense_periods.insert_one(period_doc)
    
    return ExpensePeriodResponse(
        **{k: v for k, v in period_doc.items() if k != "_id"},
        project_name=project["name"],
        expected_items_count=0,
        total_monthly_income=0.0,
        total_monthly_expenses=0.0
    )


@router.get("/periods", response_model=ExpensePeriodListResponse)
async def list_expense_periods(
    project_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """List all expense periods"""
    query = {"user_id": current_user["id"]}
    if project_id:
        query["project_id"] = project_id
    
    periods = await db.expense_periods.find(query, {"_id": 0}).sort("start_month", -1).to_list(1000)
    
    result = []
    for period in periods:
        project = await db.projects.find_one({"id": period["project_id"]}, {"_id": 0, "name": 1})
        
        # Count items and calculate totals
        items = await db.expected_items.find({"period_id": period["id"]}, {"_id": 0}).to_list(1000)
        
        monthly_income = 0.0
        monthly_expenses = 0.0
        for item in items:
            if item["frequency"] == "monthly":
                if item["item_type"] == "income":
                    monthly_income += item["amount"]
                else:
                    monthly_expenses += item["amount"]
            elif item["frequency"] == "yearly":
                # Spread yearly over 12 months
                if item["item_type"] == "income":
                    monthly_income += item["amount"] / 12
                else:
                    monthly_expenses += item["amount"] / 12
        
        result.append(ExpensePeriodResponse(
            **period,
            project_name=project["name"] if project else None,
            expected_items_count=len(items),
            total_monthly_income=round(monthly_income, 2),
            total_monthly_expenses=round(monthly_expenses, 2)
        ))
    
    return ExpensePeriodListResponse(periods=result, total=len(result))


@router.get("/periods/{period_id}", response_model=ExpensePeriodResponse)
async def get_expense_period(period_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific expense period"""
    period = await db.expense_periods.find_one(
        {"id": period_id, "user_id": current_user["id"]}, {"_id": 0}
    )
    if not period:
        raise HTTPException(status_code=404, detail="Expense period not found")
    
    project = await db.projects.find_one({"id": period["project_id"]}, {"_id": 0, "name": 1})
    items = await db.expected_items.find({"period_id": period_id}, {"_id": 0}).to_list(1000)
    
    monthly_income = 0.0
    monthly_expenses = 0.0
    for item in items:
        if item["frequency"] == "monthly":
            if item["item_type"] == "income":
                monthly_income += item["amount"]
            else:
                monthly_expenses += item["amount"]
        elif item["frequency"] == "yearly":
            if item["item_type"] == "income":
                monthly_income += item["amount"] / 12
            else:
                monthly_expenses += item["amount"] / 12
    
    return ExpensePeriodResponse(
        **period,
        project_name=project["name"] if project else None,
        expected_items_count=len(items),
        total_monthly_income=round(monthly_income, 2),
        total_monthly_expenses=round(monthly_expenses, 2)
    )


@router.put("/periods/{period_id}", response_model=ExpensePeriodResponse)
async def update_expense_period(
    period_id: str, data: ExpensePeriodUpdate, current_user: dict = Depends(get_current_user)
):
    """Update an expense period"""
    period = await db.expense_periods.find_one({"id": period_id, "user_id": current_user["id"]})
    if not period:
        raise HTTPException(status_code=404, detail="Expense period not found")
    
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    
    # Validate months if provided
    if "start_month" in update_data or "end_month" in update_data:
        start = update_data.get("start_month", period["start_month"])
        end = update_data.get("end_month", period["end_month"])
        try:
            datetime.strptime(start, "%Y-%m")
            datetime.strptime(end, "%Y-%m")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid month format. Use YYYY-MM")
        if start > end:
            raise HTTPException(status_code=400, detail="Start month must be before end month")
    
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.expense_periods.update_one({"id": period_id}, {"$set": update_data})
    return await get_expense_period(period_id, current_user)


@router.delete("/periods/{period_id}", response_model=MessageResponse)
async def delete_expense_period(period_id: str, current_user: dict = Depends(get_current_user)):
    """Delete an expense period and all its expected items"""
    period = await db.expense_periods.find_one({"id": period_id, "user_id": current_user["id"]})
    if not period:
        raise HTTPException(status_code=404, detail="Expense period not found")
    
    # Delete all expected items in this period
    await db.expected_items.delete_many({"period_id": period_id})
    await db.expense_periods.delete_one({"id": period_id})
    
    return MessageResponse(message="Expense period and all items deleted")


# ============ EXPECTED ITEMS ============

@router.get("/periods/{period_id}/items", response_model=ExpectedItemListResponse)
async def get_period_items(period_id: str, current_user: dict = Depends(get_current_user)):
    """Get all expected items for a specific expense period"""
    period = await db.expense_periods.find_one({"id": period_id, "user_id": current_user["id"]})
    if not period:
        raise HTTPException(status_code=404, detail="Expense period not found")
    
    items = await db.expected_items.find({"period_id": period_id}, {"_id": 0}).to_list(1000)
    
    project = await db.projects.find_one({"id": period["project_id"]}, {"_id": 0, "name": 1})
    
    result = []
    for item in items:
        category = None
        if item.get("category_id"):
            category = await db.finance_categories.find_one({"id": item["category_id"]}, {"_id": 0, "name": 1})
        
        result.append(ExpectedItemResponse(
            **item,
            period_name=period["name"],
            project_name=project["name"] if project else None,
            category_name=category["name"] if category else None
        ))
    
    # Sort by type (income first) then by amount descending
    result.sort(key=lambda x: (0 if x.item_type == "income" else 1, -x.amount))
    
    return ExpectedItemListResponse(items=result, total=len(result))


@router.post("/items", response_model=ExpectedItemResponse)
async def create_expected_item(data: ExpectedItemCreate, current_user: dict = Depends(get_current_user)):
    """Create a new expected item (income or expense) within a period"""
    period = await db.expense_periods.find_one({"id": data.period_id, "user_id": current_user["id"]})
    if not period:
        raise HTTPException(status_code=404, detail="Expense period not found")
    
    # Validate category if provided
    category = None
    if data.category_id:
        category = await db.finance_categories.find_one({"id": data.category_id, "user_id": current_user["id"]})
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
    
    item_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    item_doc = {
        "id": item_id,
        "user_id": current_user["id"],
        "period_id": data.period_id,
        "project_id": period["project_id"],
        "name": data.name,
        "amount": abs(data.amount),  # Always store positive
        "item_type": data.item_type.value,
        "frequency": data.frequency.value,
        "category_id": data.category_id,
        "month": data.month,
        "notes": data.notes,
        "created_at": now,
        "updated_at": now
    }
    
    await db.expected_items.insert_one(item_doc)
    
    project = await db.projects.find_one({"id": period["project_id"]}, {"_id": 0, "name": 1})
    
    return ExpectedItemResponse(
        **{k: v for k, v in item_doc.items() if k != "_id"},
        period_name=period["name"],
        project_name=project["name"] if project else None,
        category_name=category["name"] if category else None
    )


@router.get("/items", response_model=ExpectedItemListResponse)
async def list_expected_items(
    period_id: Optional[str] = None,
    project_id: Optional[str] = None,
    item_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """List expected items"""
    query = {"user_id": current_user["id"]}
    if period_id:
        query["period_id"] = period_id
    if project_id:
        query["project_id"] = project_id
    if item_type:
        query["item_type"] = item_type
    
    items = await db.expected_items.find(query, {"_id": 0}).to_list(1000)
    
    result = []
    for item in items:
        period = await db.expense_periods.find_one({"id": item["period_id"]}, {"_id": 0, "name": 1})
        project = await db.projects.find_one({"id": item["project_id"]}, {"_id": 0, "name": 1})
        category = None
        if item.get("category_id"):
            category = await db.finance_categories.find_one({"id": item["category_id"]}, {"_id": 0, "name": 1})
        
        result.append(ExpectedItemResponse(
            **item,
            period_name=period["name"] if period else None,
            project_name=project["name"] if project else None,
            category_name=category["name"] if category else None
        ))
    
    return ExpectedItemListResponse(items=result, total=len(result))


@router.put("/items/{item_id}", response_model=ExpectedItemResponse)
async def update_expected_item(
    item_id: str, data: ExpectedItemUpdate, current_user: dict = Depends(get_current_user)
):
    """Update an expected item"""
    item = await db.expected_items.find_one({"id": item_id, "user_id": current_user["id"]})
    if not item:
        raise HTTPException(status_code=404, detail="Expected item not found")
    
    update_data = {k: v.value if hasattr(v, 'value') else v for k, v in data.model_dump().items() if v is not None}
    if "amount" in update_data:
        update_data["amount"] = abs(update_data["amount"])
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.expected_items.update_one({"id": item_id}, {"$set": update_data})
    
    updated = await db.expected_items.find_one({"id": item_id}, {"_id": 0})
    period = await db.expense_periods.find_one({"id": updated["period_id"]}, {"_id": 0, "name": 1})
    project = await db.projects.find_one({"id": updated["project_id"]}, {"_id": 0, "name": 1})
    category = None
    if updated.get("category_id"):
        category = await db.finance_categories.find_one({"id": updated["category_id"]}, {"_id": 0, "name": 1})
    
    return ExpectedItemResponse(
        **updated,
        period_name=period["name"] if period else None,
        project_name=project["name"] if project else None,
        category_name=category["name"] if category else None
    )


@router.delete("/items/{item_id}", response_model=MessageResponse)
async def delete_expected_item(item_id: str, current_user: dict = Depends(get_current_user)):
    """Delete an expected item"""
    item = await db.expected_items.find_one({"id": item_id, "user_id": current_user["id"]})
    if not item:
        raise HTTPException(status_code=404, detail="Expected item not found")
    
    await db.expected_items.delete_one({"id": item_id})
    return MessageResponse(message="Expected item deleted")


# ============ MONTHLY BUDGET COMPARISON ============

@router.get("/comparison", response_model=MonthlyBudgetComparison)
async def get_monthly_budget_comparison(
    month: str = Query(..., description="Month in YYYY-MM format"),
    project_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Get budget comparison for a specific month.
    Finds the active expense period for that month and compares expected vs actual.
    """
    # Validate month
    try:
        datetime.strptime(month, "%Y-%m")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid month format. Use YYYY-MM")
    
    # Find active period for this month
    period_query = {
        "user_id": current_user["id"],
        "start_month": {"$lte": month},
        "end_month": {"$gte": month}
    }
    if project_id:
        period_query["project_id"] = project_id
    
    period = await db.expense_periods.find_one(period_query, {"_id": 0})
    
    # Get expected items for the period
    expected_items = []
    if period:
        items_query = {"period_id": period["id"]}
        expected_items = await db.expected_items.find(items_query, {"_id": 0}).to_list(1000)
    
    # Get actual transactions for the month
    month_start = f"{month}-01"
    year, mon = map(int, month.split("-"))
    next_month = datetime(year, mon, 1) + relativedelta(months=1)
    month_end = (next_month - relativedelta(days=1)).strftime("%Y-%m-%d")
    
    tx_query = {
        "user_id": current_user["id"],
        "date": {"$gte": month_start, "$lte": month_end}
    }
    if project_id:
        tx_query["project_id"] = project_id
    
    transactions = await db.finance_transactions.find(tx_query, {"_id": 0}).to_list(10000)
    
    # Get categories for type lookup
    cat_ids = list(set([t.get("category_id") for t in transactions if t.get("category_id")]))
    categories = await db.finance_categories.find({"id": {"$in": cat_ids}}, {"_id": 0}).to_list(1000)
    cat_map = {c["id"]: c for c in categories}
    
    # Calculate expected totals
    expected_income = 0.0
    expected_expenses = 0.0
    budget_items = []
    used_transaction_ids = set()
    
    for item in expected_items:
        # Determine if this item applies to this month
        applies = False
        if item["frequency"] == "monthly":
            applies = True
        elif item["frequency"] == "yearly":
            # Check if this is the right month
            item_month = item.get("month", "01")  # Default to January
            if len(item_month) == 2:  # Just MM
                applies = item_month == month[5:7]
            else:  # YYYY-MM
                applies = item_month == month
        elif item["frequency"] == "one_time":
            item_month = item.get("month", "")
            applies = item_month == month
        
        if not applies:
            continue
        
        amount = item["amount"]
        if item["item_type"] == "income":
            expected_income += amount
        else:
            expected_expenses += amount
        
        # Find matching transactions
        matched_txs = []
        actual_amount = 0.0
        
        for tx in transactions:
            if tx["id"] in used_transaction_ids:
                continue
            
            # Match by category if available
            if item.get("category_id") and tx.get("category_id") == item["category_id"]:
                matched_txs.append({
                    "id": tx["id"],
                    "date": tx["date"],
                    "amount": tx["amount"],
                    "notes": tx.get("notes")
                })
                actual_amount += abs(tx["amount"])
                used_transaction_ids.add(tx["id"])
            # Or match by similar amount and type
            elif not item.get("category_id"):
                tx_is_income = tx["amount"] > 0
                item_is_income = item["item_type"] == "income"
                amount_diff = abs(abs(tx["amount"]) - amount)
                tolerance = amount * 0.15  # 15% tolerance
                
                if tx_is_income == item_is_income and amount_diff <= tolerance:
                    matched_txs.append({
                        "id": tx["id"],
                        "date": tx["date"],
                        "amount": tx["amount"],
                        "notes": tx.get("notes")
                    })
                    actual_amount += abs(tx["amount"])
                    used_transaction_ids.add(tx["id"])
        
        budget_items.append(MonthlyBudgetItem(
            expected_item_id=item["id"],
            name=item["name"],
            item_type=item["item_type"],
            frequency=item["frequency"],
            expected_amount=amount,
            actual_amount=round(actual_amount, 2),
            difference=round(actual_amount - amount, 2),
            is_matched=len(matched_txs) > 0,
            matched_transactions=matched_txs
        ))
    
    # Calculate actual totals from ALL transactions
    actual_income = 0.0
    actual_expenses = 0.0
    unmatched = []
    
    for tx in transactions:
        cat = cat_map.get(tx.get("category_id"), {})
        cat_type = cat.get("type", "expense")
        
        if tx["amount"] > 0 or cat_type == "income":
            actual_income += abs(tx["amount"])
        else:
            actual_expenses += abs(tx["amount"])
        
        if tx["id"] not in used_transaction_ids:
            unmatched.append({
                "id": tx["id"],
                "date": tx["date"],
                "amount": tx["amount"],
                "notes": tx.get("notes"),
                "category": cat.get("name", "Unknown")
            })
    
    # Sort items: unmatched first, then by amount
    budget_items.sort(key=lambda x: (x.is_matched, -x.expected_amount))
    
    return MonthlyBudgetComparison(
        month=month,
        period_id=period["id"] if period else None,
        period_name=period["name"] if period else None,
        expected_income=round(expected_income, 2),
        expected_expenses=round(expected_expenses, 2),
        expected_profit=round(expected_income - expected_expenses, 2),
        actual_income=round(actual_income, 2),
        actual_expenses=round(actual_expenses, 2),
        actual_profit=round(actual_income - actual_expenses, 2),
        income_difference=round(actual_income - expected_income, 2),
        expense_difference=round(actual_expenses - expected_expenses, 2),
        profit_difference=round((actual_income - actual_expenses) - (expected_income - expected_expenses), 2),
        items=budget_items,
        unmatched_transactions=unmatched
    )
