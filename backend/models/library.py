"""Library related Pydantic models."""
from pydantic import BaseModel, Field
from typing import List, Optional


class LibraryFolderCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    parent_id: Optional[str] = None


class LibraryFolderUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    parent_id: Optional[str] = None


class LibraryFolderResponse(BaseModel):
    id: str
    project_id: str
    name: str
    parent_id: Optional[str] = None
    created_at: str
    updated_at: str


class LibraryEntryCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=10000)
    folder_id: Optional[str] = None
    is_public: bool = False


class LibraryEntryUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=10000)
    folder_id: Optional[str] = None
    is_public: Optional[bool] = None


class LibraryEntryResponse(BaseModel):
    id: str
    project_id: str
    folder_id: Optional[str] = None
    title: str
    description: str
    is_public: bool
    views: int = 0
    created_at: str
    updated_at: str


class LibraryListResponse(BaseModel):
    folders: List[LibraryFolderResponse]
    entries: List[LibraryEntryResponse]
