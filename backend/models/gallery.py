"""Gallery related Pydantic models."""
from pydantic import BaseModel, Field
from typing import List, Optional


class GalleryFolderCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    parent_id: Optional[str] = None
    is_public: bool = False


class GalleryFolderUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    parent_id: Optional[str] = None
    is_public: Optional[bool] = None


class GalleryFolderResponse(BaseModel):
    id: str
    project_id: str
    name: str
    parent_id: Optional[str] = None
    is_public: bool = False
    created_at: str
    updated_at: str


class GalleryImageResponse(BaseModel):
    id: str
    project_id: str
    folder_id: Optional[str] = None
    filename: str
    url: str
    created_at: str


class GalleryListResponse(BaseModel):
    folders: List[GalleryFolderResponse]
    images: List[GalleryImageResponse]


class PublicGalleryResponse(BaseModel):
    folders: List[GalleryFolderResponse]
    images: List[GalleryImageResponse]
