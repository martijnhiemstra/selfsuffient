"""Blog related Pydantic models."""
from pydantic import BaseModel, Field
from typing import List, Optional


class BlogEntryCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=10000)
    is_public: bool = False


class BlogEntryUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=10000)
    is_public: Optional[bool] = None


class BlogEntryResponse(BaseModel):
    id: str
    project_id: str
    title: str
    description: str
    is_public: bool
    views: int = 0
    created_at: str
    updated_at: str


class BlogListResponse(BaseModel):
    entries: List[BlogEntryResponse]
    total: int
