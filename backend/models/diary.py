"""Diary related Pydantic models."""
from pydantic import BaseModel, Field
from typing import List, Optional


class DiaryEntryCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    story: str = Field(default="", max_length=10000)
    entry_datetime: Optional[str] = None


class DiaryEntryUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    story: Optional[str] = Field(None, max_length=10000)
    entry_datetime: Optional[str] = None


class DiaryEntryResponse(BaseModel):
    id: str
    project_id: str
    title: str
    story: str
    entry_datetime: str
    created_at: str
    updated_at: str


class DiaryListResponse(BaseModel):
    entries: List[DiaryEntryResponse]
    total: int
