"""Routine related Pydantic models."""
from pydantic import BaseModel, Field
from typing import List, Optional


class RoutineTaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)
    order: int = 0


class RoutineTaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    order: Optional[int] = None


class RoutineTaskResponse(BaseModel):
    id: str
    project_id: str
    routine_type: str  # startup or shutdown
    title: str
    description: str
    order: int
    created_at: str


class RoutineCompletionResponse(BaseModel):
    id: str
    task_id: str
    completed_date: str
    created_at: str


class RoutineListResponse(BaseModel):
    tasks: List[RoutineTaskResponse]
    completions_today: List[str]  # list of task_ids completed today
