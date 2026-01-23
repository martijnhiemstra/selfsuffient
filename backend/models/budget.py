"""Expense Period models - replacing Recurring Transactions."""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class ExpenseFrequency(str, Enum):
    monthly = "monthly"
    yearly = "yearly"
    one_time = "one_time"


class ExpenseType(str, Enum):
    income = "income"
    expense = "expense"


# Expense Period models
class ExpensePeriodCreate(BaseModel):
    project_id: str
    name: str  # e.g., "2024", "First Year on Farm"
    start_month: str  # YYYY-MM format
    end_month: str  # YYYY-MM format
    notes: Optional[str] = None


class ExpensePeriodUpdate(BaseModel):
    name: Optional[str] = None
    start_month: Optional[str] = None
    end_month: Optional[str] = None
    notes: Optional[str] = None


class ExpensePeriodResponse(BaseModel):
    id: str
    project_id: str
    project_name: Optional[str] = None
    name: str
    start_month: str
    end_month: str
    notes: Optional[str] = None
    expected_items_count: int = 0
    total_monthly_income: float = 0.0
    total_monthly_expenses: float = 0.0
    created_at: str
    updated_at: str


class ExpensePeriodListResponse(BaseModel):
    periods: List[ExpensePeriodResponse]
    total: int


# Expected Item models (income or expense within a period)
class ExpectedItemCreate(BaseModel):
    period_id: str
    name: str  # e.g., "Rent", "Salary", "Electricity"
    amount: float  # positive number, type determines if income/expense
    item_type: ExpenseType  # income or expense
    frequency: ExpenseFrequency  # monthly, yearly, one_time
    category_id: Optional[str] = None
    month: Optional[str] = None  # For one_time or yearly, specify which month (MM or YYYY-MM)
    notes: Optional[str] = None


class ExpectedItemUpdate(BaseModel):
    name: Optional[str] = None
    amount: Optional[float] = None
    item_type: Optional[ExpenseType] = None
    frequency: Optional[ExpenseFrequency] = None
    category_id: Optional[str] = None
    month: Optional[str] = None
    notes: Optional[str] = None


class ExpectedItemResponse(BaseModel):
    id: str
    period_id: str
    period_name: Optional[str] = None
    project_id: str
    project_name: Optional[str] = None
    name: str
    amount: float
    item_type: ExpenseType
    frequency: ExpenseFrequency
    category_id: Optional[str] = None
    category_name: Optional[str] = None
    month: Optional[str] = None
    notes: Optional[str] = None
    created_at: str
    updated_at: str


class ExpectedItemListResponse(BaseModel):
    items: List[ExpectedItemResponse]
    total: int


# Monthly Budget Comparison
class MonthlyBudgetItem(BaseModel):
    expected_item_id: str
    name: str
    item_type: str
    frequency: str
    expected_amount: float
    actual_amount: float
    difference: float
    is_matched: bool
    matched_transactions: List[dict] = []


class MonthlyBudgetComparison(BaseModel):
    month: str
    period_id: Optional[str] = None
    period_name: Optional[str] = None
    expected_income: float
    expected_expenses: float
    expected_profit: float
    actual_income: float
    actual_expenses: float
    actual_profit: float
    income_difference: float
    expense_difference: float
    profit_difference: float
    items: List[MonthlyBudgetItem]
    unmatched_transactions: List[dict] = []
