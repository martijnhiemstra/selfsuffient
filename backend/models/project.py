"""Project related Pydantic models."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=5000)
    is_public: bool = False
    languages: List[str] = Field(default=["en"])
    primary_language: str = Field(default="en")


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    is_public: Optional[bool] = None
    languages: Optional[List[str]] = None
    primary_language: Optional[str] = None


class ProjectResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: str
    image: Optional[str] = None
    is_public: bool
    languages: List[str] = ["en"]
    primary_language: str = "en"
    created_at: str
    updated_at: str


class ProjectListResponse(BaseModel):
    projects: List[ProjectResponse]
    total: int
