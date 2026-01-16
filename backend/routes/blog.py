"""Blog routes."""
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from datetime import datetime, timezone
import uuid

from config import db
from models import BlogEntryCreate, BlogEntryUpdate, BlogEntryResponse, BlogListResponse, MessageResponse
from services import get_current_user, verify_project_access

router = APIRouter()


@router.post("/projects/{project_id}/blog", response_model=BlogEntryResponse)
async def create_blog_entry(
    project_id: str,
    data: BlogEntryCreate,
    current_user: dict = Depends(get_current_user)
):
    await verify_project_access(project_id, current_user["id"])
    
    entry_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    entry_doc = {
        "id": entry_id,
        "project_id": project_id,
        "title": data.title,
        "description": data.description,
        "is_public": data.is_public,
        "views": 0,
        "created_at": now,
        "updated_at": now
    }
    
    await db.blog_entries.insert_one(entry_doc)
    return BlogEntryResponse(**{k: v for k, v in entry_doc.items() if k != "_id"})


@router.get("/projects/{project_id}/blog", response_model=BlogListResponse)
async def list_blog_entries(
    project_id: str,
    search: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    current_user: dict = Depends(get_current_user)
):
    await verify_project_access(project_id, current_user["id"])
    
    query = {"project_id": project_id}
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    sort_direction = -1 if sort_order == "desc" else 1
    total = await db.blog_entries.count_documents(query)
    entries = await db.blog_entries.find(query, {"_id": 0}).sort(sort_by, sort_direction).to_list(1000)
    
    return BlogListResponse(entries=[BlogEntryResponse(**e) for e in entries], total=total)


@router.get("/projects/{project_id}/blog/{entry_id}", response_model=BlogEntryResponse)
async def get_blog_entry(
    project_id: str,
    entry_id: str,
    current_user: dict = Depends(get_current_user)
):
    await verify_project_access(project_id, current_user["id"])
    
    entry = await db.blog_entries.find_one({"id": entry_id, "project_id": project_id}, {"_id": 0})
    if not entry:
        raise HTTPException(status_code=404, detail="Blog entry not found")
    
    return BlogEntryResponse(**entry)


@router.put("/projects/{project_id}/blog/{entry_id}", response_model=BlogEntryResponse)
async def update_blog_entry(
    project_id: str,
    entry_id: str,
    data: BlogEntryUpdate,
    current_user: dict = Depends(get_current_user)
):
    await verify_project_access(project_id, current_user["id"])
    
    entry = await db.blog_entries.find_one({"id": entry_id, "project_id": project_id})
    if not entry:
        raise HTTPException(status_code=404, detail="Blog entry not found")
    
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.blog_entries.update_one({"id": entry_id}, {"$set": update_data})
    updated = await db.blog_entries.find_one({"id": entry_id}, {"_id": 0})
    return BlogEntryResponse(**updated)


@router.delete("/projects/{project_id}/blog/{entry_id}", response_model=MessageResponse)
async def delete_blog_entry(
    project_id: str,
    entry_id: str,
    current_user: dict = Depends(get_current_user)
):
    await verify_project_access(project_id, current_user["id"])
    
    result = await db.blog_entries.delete_one({"id": entry_id, "project_id": project_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Blog entry not found")
    
    return MessageResponse(message="Blog entry deleted")
