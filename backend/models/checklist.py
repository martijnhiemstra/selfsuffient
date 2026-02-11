"""Checklist models for projects."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ChecklistItemCreate(BaseModel):
    """Create a checklist item."""
    text: str
    order: int = 0


class ChecklistItemUpdate(BaseModel):
    """Update a checklist item."""
    text: Optional[str] = None
    is_done: Optional[bool] = None
    order: Optional[int] = None


class ChecklistItemResponse(BaseModel):
    """Response for a checklist item."""
    id: str
    checklist_id: str
    text: str
    is_done: bool = False
    order: int = 0
    created_at: str
    updated_at: str


class ChecklistCreate(BaseModel):
    """Create a checklist."""
    project_id: str
    name: str
    description: Optional[str] = None


class ChecklistUpdate(BaseModel):
    """Update a checklist."""
    name: Optional[str] = None
    description: Optional[str] = None


class ChecklistResponse(BaseModel):
    """Response for a checklist."""
    id: str
    project_id: str
    project_name: Optional[str] = None
    name: str
    description: Optional[str] = None
    items: List[ChecklistItemResponse] = []
    total_items: int = 0
    completed_items: int = 0
    created_at: str
    updated_at: str


class ChecklistListResponse(BaseModel):
    """Response for list of checklists."""
    checklists: List[ChecklistResponse]
    total: int
