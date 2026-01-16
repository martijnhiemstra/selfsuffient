"""Task related Pydantic models."""
from pydantic import BaseModel, Field
from typing import List, Optional


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=5000)
    task_datetime: str
    is_all_day: bool = False
    recurrence: Optional[str] = None  # none, daily, weekly, monthly, yearly


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    task_datetime: Optional[str] = None
    is_all_day: Optional[bool] = None
    recurrence: Optional[str] = None


class TaskResponse(BaseModel):
    id: str
    project_id: str
    title: str
    description: str
    task_datetime: str
    is_all_day: bool
    recurrence: Optional[str] = None
    created_at: str
    updated_at: str


class TaskListResponse(BaseModel):
    tasks: List[TaskResponse]
    total: int
