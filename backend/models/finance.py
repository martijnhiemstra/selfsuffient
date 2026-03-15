"""Finance models."""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class AccountType(str, Enum):
    bank = "bank"
    cash = "cash"
    crypto = "crypto"
    asset = "asset"


class CategoryType(str, Enum):
    income = "income"
    expense = "expense"
    investment = "investment"


class RecurringFrequency(str, Enum):
    monthly = "monthly"
    yearly = "yearly"


# Account models
class AccountCreate(BaseModel):
    project_id: str
    name: str
    type: AccountType
    starting_balance: float = 0.0  # Initial capital in the account
    notes: Optional[str] = None


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[AccountType] = None
    starting_balance: Optional[float] = None
    notes: Optional[str] = None


class AccountResponse(BaseModel):
    id: str
    project_id: str
    name: str
    type: AccountType
    starting_balance: float = 0.0
    notes: Optional[str] = None
    balance: float = 0.0  # Current balance = starting_balance + sum(transactions)
    created_at: str
    updated_at: str


class AccountListResponse(BaseModel):
    accounts: List[AccountResponse]
    total: int


# Category models
class CategoryCreate(BaseModel):
    project_id: str
    name: str
    type: CategoryType


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[CategoryType] = None


class CategoryResponse(BaseModel):
    id: str
    project_id: str
    name: str
    type: CategoryType
    created_at: str


class CategoryListResponse(BaseModel):
    categories: List[CategoryResponse]
    total: int


# Transaction models
class TransactionCreate(BaseModel):
    date: str
    amount: float  # positive = income, negative = expense
    account_id: str
    project_id: str
    category_id: str
    notes: Optional[str] = None
    linked_transaction_id: Optional[str] = None  # For transfers
    savings_goal_id: Optional[str] = None  # Link to savings goal


class TransactionUpdate(BaseModel):
    date: Optional[str] = None
    amount: Optional[float] = None
    account_id: Optional[str] = None
    category_id: Optional[str] = None
    notes: Optional[str] = None
    savings_goal_id: Optional[str] = None  # Can attach/detach from savings goal


class TransactionResponse(BaseModel):
    id: str
    date: str
    amount: float
    account_id: str
    account_name: Optional[str] = None
    project_id: str
    project_name: Optional[str] = None
    category_id: str
    category_name: Optional[str] = None
    category_type: Optional[str] = None
    notes: Optional[str] = None
    linked_transaction_id: Optional[str] = None
    savings_goal_id: Optional[str] = None
    savings_goal_name: Optional[str] = None
    created_at: str
    updated_at: str


class TransactionListResponse(BaseModel):
    transactions: List[TransactionResponse]
    total: int


# Recurring Transaction models
class RecurringTransactionCreate(BaseModel):
    name: str
    amount: float
    frequency: RecurringFrequency
    start_date: str
    account_id: str
    project_id: str
    category_id: str
    active: bool = True


class RecurringTransactionUpdate(BaseModel):
    name: Optional[str] = None
    amount: Optional[float] = None
    frequency: Optional[RecurringFrequency] = None
    start_date: Optional[str] = None
    account_id: Optional[str] = None
    category_id: Optional[str] = None
    active: Optional[bool] = None


class RecurringTransactionResponse(BaseModel):
    id: str
    name: str
    amount: float
    frequency: RecurringFrequency
    start_date: str
    next_execution_date: str
    account_id: str
    account_name: Optional[str] = None
    project_id: str
    project_name: Optional[str] = None
    category_id: str
    category_name: Optional[str] = None
    active: bool
    created_at: str
    updated_at: str


class RecurringTransactionListResponse(BaseModel):
    recurring_transactions: List[RecurringTransactionResponse]
    total: int


# Dashboard & Analytics models
class ProjectFinanceSummary(BaseModel):
    project_id: str
    project_name: str
    total_income: float
    total_expenses: float
    total_investments: float
    net_balance: float
    avg_monthly_burn: float
    months_active: int


class MonthlyOverview(BaseModel):
    month: str  # YYYY-MM format
    total_income: float
    total_expenses: float
    total_investments: float
    net_result: float
    by_project: List[dict]
    by_category: List[dict]


class RunwayCalculation(BaseModel):
    total_liquid_cash: float
    avg_monthly_burn: float
    runway_months: float
    safety_threshold: float
    is_below_threshold: bool
    accounts_included: List[dict]


# Default categories to seed
DEFAULT_CATEGORIES = [
    {"name": "Income", "type": "income"},
    {"name": "Rent", "type": "expense"},
    {"name": "Food", "type": "expense"},
    {"name": "Utilities", "type": "expense"},
    {"name": "Transport", "type": "expense"},
    {"name": "Animals", "type": "expense"},
    {"name": "Tools", "type": "expense"},
    {"name": "Infrastructure", "type": "expense"},
    {"name": "Land", "type": "investment"},
    {"name": "Investment", "type": "investment"},
    {"name": "Misc", "type": "expense"},
]


# Savings Goal models
class SavingsGoalCreate(BaseModel):
    project_id: str
    name: str
    description: Optional[str] = Field(None, max_length=2000)
    target_amount: float


class SavingsGoalUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = Field(None, max_length=2000)
    target_amount: Optional[float] = None


class SavingsGoalResponse(BaseModel):
    id: str
    project_id: str
    project_name: Optional[str] = None
    name: str
    description: Optional[str] = None
    target_amount: float
    current_amount: float = 0.0
    progress_percent: float = 0.0
    created_at: str
    updated_at: str


class SavingsGoalListResponse(BaseModel):
    savings_goals: List[SavingsGoalResponse]
    total: int


# Import models
class ImportedTransaction(BaseModel):
    """A single transaction parsed from import file"""
    date: str
    amount: float
    description: Optional[str] = None
    memo: Optional[str] = None
    payee: Optional[str] = None
    ref_number: Optional[str] = None  # Check number, reference ID, etc.
    transaction_type: Optional[str] = None  # Credit/Debit/etc.
    # Duplicate detection
    is_potential_duplicate: Optional[bool] = None
    duplicate_of_id: Optional[str] = None
    duplicate_reason: Optional[str] = None
    # AI analysis fields
    ai_category: Optional[str] = None
    ai_type: Optional[str] = None  # "income" or "expense"
    ai_is_recurring: Optional[bool] = None
    ai_recurring_frequency: Optional[str] = None
    ai_is_unusual: Optional[bool] = None
    ai_unusual_reason: Optional[str] = None
    ai_confidence: Optional[float] = None


class CSVColumnMapping(BaseModel):
    """Mapping of CSV columns to transaction fields"""
    date_column: str
    amount_column: str
    description_column: Optional[str] = None
    memo_column: Optional[str] = None
    date_format: str = "%Y-%m-%d"  # Python strptime format
    amount_is_negative_expense: bool = True  # If true, negative = expense
    has_header: bool = True
    delimiter: str = ","


class ImportPreviewRequest(BaseModel):
    """Request to preview imported transactions"""
    file_type: str  # "csv" or "ofx"
    column_mapping: Optional[CSVColumnMapping] = None  # Only for CSV


class ImportPreviewResponse(BaseModel):
    """Response with parsed transactions preview"""
    transactions: List[ImportedTransaction]
    total: int
    columns: Optional[List[str]] = None  # For CSV, the detected columns
    warnings: List[str] = []
    ai_analyzed: bool = False  # Whether AI analysis was performed


class ImportConfirmRequest(BaseModel):
    """Request to confirm and save imported transactions"""
    transactions: List[ImportedTransaction]
    project_id: str
    account_id: str
    default_category_id: str  # Default category for all imported transactions
