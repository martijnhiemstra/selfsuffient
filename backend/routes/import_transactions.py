"""Transaction import routes - CSV and OFX file parsing."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Optional, List
from datetime import datetime, timezone
import uuid
import csv
import io
import re

from config import db
from models import (
    ImportedTransaction, CSVColumnMapping, ImportPreviewResponse,
    ImportConfirmRequest, TransactionResponse, MessageResponse
)
from services import get_current_user

router = APIRouter()


def parse_date(date_str: str, date_format: str = "%Y-%m-%d") -> str:
    """Parse date string and return ISO format YYYY-MM-DD"""
    # Common date formats to try
    formats_to_try = [
        date_format,
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%d.%m.%Y",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%m-%d-%Y",
        "%Y%m%d",
    ]
    
    date_str = date_str.strip()
    
    for fmt in formats_to_try:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    
    raise ValueError(f"Cannot parse date: {date_str}")


def parse_amount(amount_str: str) -> float:
    """Parse amount string handling various formats"""
    # Remove currency symbols and whitespace
    amount_str = re.sub(r'[€$£¥₹\s]', '', amount_str.strip())
    
    # Handle European format (1.234,56 -> 1234.56)
    if ',' in amount_str and '.' in amount_str:
        # Determine which is decimal separator
        if amount_str.rfind(',') > amount_str.rfind('.'):
            # European: 1.234,56
            amount_str = amount_str.replace('.', '').replace(',', '.')
        else:
            # US: 1,234.56
            amount_str = amount_str.replace(',', '')
    elif ',' in amount_str:
        # Could be European decimal or US thousands
        # If comma is followed by exactly 2 digits at end, treat as decimal
        if re.match(r'^-?[\d.]*,\d{2}$', amount_str):
            amount_str = amount_str.replace(',', '.')
        else:
            amount_str = amount_str.replace(',', '')
    
    return float(amount_str)


@router.post("/preview/csv", response_model=ImportPreviewResponse)
async def preview_csv_import(
    file: UploadFile = File(...),
    delimiter: str = Form(","),
    has_header: bool = Form(True),
    date_column: Optional[str] = Form(None),
    amount_column: Optional[str] = Form(None),
    description_column: Optional[str] = Form(None),
    date_format: str = Form("%Y-%m-%d"),
    current_user: dict = Depends(get_current_user)
):
    """
    Preview CSV file import. 
    First call without column mappings to get column names,
    then call again with mappings to get parsed transactions.
    """
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV file")
    
    content = await file.read()
    try:
        text = content.decode('utf-8')
    except UnicodeDecodeError:
        try:
            text = content.decode('latin-1')
        except:
            raise HTTPException(status_code=400, detail="Cannot decode file. Please use UTF-8 or Latin-1 encoding.")
    
    # Parse CSV
    reader = csv.reader(io.StringIO(text), delimiter=delimiter)
    rows = list(reader)
    
    if len(rows) == 0:
        raise HTTPException(status_code=400, detail="CSV file is empty")
    
    columns = []
    data_rows = rows
    
    if has_header:
        columns = [col.strip() for col in rows[0]]
        data_rows = rows[1:]
    else:
        # Generate column names
        columns = [f"Column {i+1}" for i in range(len(rows[0]))]
    
    # If no column mappings provided, just return columns for user to map
    if not date_column or not amount_column:
        return ImportPreviewResponse(
            transactions=[],
            total=len(data_rows),
            columns=columns,
            warnings=["Please map the date and amount columns to continue."]
        )
    
    # Parse transactions
    transactions = []
    warnings = []
    
    try:
        date_idx = columns.index(date_column)
        amount_idx = columns.index(amount_column)
        desc_idx = columns.index(description_column) if description_column and description_column in columns else None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Column not found: {str(e)}")
    
    for row_num, row in enumerate(data_rows, start=2 if has_header else 1):
        if len(row) <= max(date_idx, amount_idx, desc_idx or 0):
            warnings.append(f"Row {row_num}: Not enough columns, skipping")
            continue
        
        try:
            date = parse_date(row[date_idx], date_format)
            amount = parse_amount(row[amount_idx])
            description = row[desc_idx].strip() if desc_idx is not None else None
            
            transactions.append(ImportedTransaction(
                date=date,
                amount=amount,
                description=description,
                memo=description
            ))
        except ValueError as e:
            warnings.append(f"Row {row_num}: {str(e)}")
        except Exception as e:
            warnings.append(f"Row {row_num}: Error parsing - {str(e)}")
    
    return ImportPreviewResponse(
        transactions=transactions,
        total=len(transactions),
        columns=columns,
        warnings=warnings[:20]  # Limit warnings to first 20
    )


@router.post("/preview/ofx", response_model=ImportPreviewResponse)
async def preview_ofx_import(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Preview OFX/QFX file import."""
    filename = file.filename.lower()
    if not (filename.endswith('.ofx') or filename.endswith('.qfx')):
        raise HTTPException(status_code=400, detail="File must be an OFX or QFX file")
    
    try:
        from ofxparse import OfxParser
    except ImportError:
        raise HTTPException(status_code=500, detail="OFX parsing library not installed")
    
    content = await file.read()
    
    try:
        # Try to parse OFX
        ofx = OfxParser.parse(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cannot parse OFX file: {str(e)}")
    
    transactions = []
    warnings = []
    
    # OFX can have multiple accounts
    if hasattr(ofx, 'account') and ofx.account:
        accounts = [ofx.account]
    elif hasattr(ofx, 'accounts') and ofx.accounts:
        accounts = ofx.accounts
    else:
        raise HTTPException(status_code=400, detail="No accounts found in OFX file")
    
    for account in accounts:
        if not hasattr(account, 'statement') or not account.statement:
            continue
        
        statement = account.statement
        if not hasattr(statement, 'transactions'):
            continue
        
        for tx in statement.transactions:
            try:
                date = tx.date.strftime("%Y-%m-%d") if tx.date else None
                if not date:
                    warnings.append(f"Transaction skipped: missing date")
                    continue
                
                amount = float(tx.amount) if tx.amount else 0
                
                # Build description from available fields
                desc_parts = []
                if hasattr(tx, 'payee') and tx.payee:
                    desc_parts.append(str(tx.payee))
                if hasattr(tx, 'memo') and tx.memo:
                    desc_parts.append(str(tx.memo))
                
                transactions.append(ImportedTransaction(
                    date=date,
                    amount=amount,
                    description=" - ".join(desc_parts) if desc_parts else None,
                    memo=str(tx.memo) if hasattr(tx, 'memo') and tx.memo else None,
                    payee=str(tx.payee) if hasattr(tx, 'payee') and tx.payee else None,
                    ref_number=str(tx.checknum) if hasattr(tx, 'checknum') and tx.checknum else None,
                    transaction_type=str(tx.type) if hasattr(tx, 'type') and tx.type else None
                ))
            except Exception as e:
                warnings.append(f"Transaction error: {str(e)}")
    
    if not transactions:
        raise HTTPException(status_code=400, detail="No transactions found in OFX file")
    
    # Sort by date
    transactions.sort(key=lambda x: x.date)
    
    return ImportPreviewResponse(
        transactions=transactions,
        total=len(transactions),
        columns=None,
        warnings=warnings[:20]
    )


@router.post("/confirm", response_model=MessageResponse)
async def confirm_import(
    data: ImportConfirmRequest,
    current_user: dict = Depends(get_current_user)
):
    """Confirm and save imported transactions."""
    # Verify project access
    project = await db.projects.find_one({"id": data.project_id, "user_id": current_user["id"]})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Verify account
    account = await db.finance_accounts.find_one({"id": data.account_id, "user_id": current_user["id"]})
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Verify category
    category = await db.finance_categories.find_one({"id": data.default_category_id, "user_id": current_user["id"]})
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    now = datetime.now(timezone.utc).isoformat()
    created_count = 0
    
    for tx in data.transactions:
        tx_id = str(uuid.uuid4())
        
        # Build notes from available fields
        notes_parts = []
        if tx.description:
            notes_parts.append(tx.description)
        if tx.payee and tx.payee not in (tx.description or ''):
            notes_parts.append(f"Payee: {tx.payee}")
        if tx.ref_number:
            notes_parts.append(f"Ref: {tx.ref_number}")
        
        tx_doc = {
            "id": tx_id,
            "user_id": current_user["id"],
            "date": tx.date,
            "amount": tx.amount,
            "account_id": data.account_id,
            "project_id": data.project_id,
            "category_id": data.default_category_id,
            "notes": " | ".join(notes_parts) if notes_parts else None,
            "linked_transaction_id": None,
            "savings_goal_id": None,
            "created_at": now,
            "updated_at": now
        }
        
        await db.finance_transactions.insert_one(tx_doc)
        created_count += 1
    
    return MessageResponse(message=f"Successfully imported {created_count} transactions")


@router.get("/sample-csv")
async def get_sample_csv():
    """Return a sample CSV format for reference."""
    return {
        "sample_format": "date,amount,description",
        "sample_rows": [
            "2024-01-15,-50.00,Grocery shopping",
            "2024-01-16,2500.00,Salary deposit",
            "2024-01-17,-120.50,Electric bill"
        ],
        "supported_date_formats": [
            "YYYY-MM-DD (2024-01-15)",
            "DD/MM/YYYY (15/01/2024)",
            "MM/DD/YYYY (01/15/2024)",
            "DD.MM.YYYY (15.01.2024)"
        ],
        "amount_notes": [
            "Positive numbers = income",
            "Negative numbers = expense",
            "Supports formats: 1234.56, 1,234.56, 1.234,56"
        ]
    }
