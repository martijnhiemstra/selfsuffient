"""Diary routes."""
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from datetime import datetime, timezone
import uuid

from config import db
from models import DiaryEntryCreate, DiaryEntryUpdate, DiaryEntryResponse, DiaryListResponse, MessageResponse
from services import get_current_user, verify_project_access

router = APIRouter()


@router.post("/projects/{project_id}/diary", response_model=DiaryEntryResponse)
async def create_diary_entry(
    project_id: str,
    data: DiaryEntryCreate,
    current_user: dict = Depends(get_current_user)
):
    await verify_project_access(project_id, current_user["id"])
    
    entry_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    entry_datetime = data.entry_datetime or now
    
    entry_doc = {
        "id": entry_id,
        "project_id": project_id,
        "title": data.title,
        "story": data.story,
        "entry_datetime": entry_datetime,
        "created_at": now,
        "updated_at": now
    }
    
    await db.diary_entries.insert_one(entry_doc)
    return DiaryEntryResponse(**{k: v for k, v in entry_doc.items() if k != "_id"})


@router.get("/projects/{project_id}/diary", response_model=DiaryListResponse)
async def list_diary_entries(
    project_id: str,
    search: Optional[str] = None,
    sort_by: str = "entry_datetime",
    sort_order: str = "desc",
    current_user: dict = Depends(get_current_user)
):
    await verify_project_access(project_id, current_user["id"])
    
    query = {"project_id": project_id}
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"story": {"$regex": search, "$options": "i"}}
        ]
    
    sort_direction = -1 if sort_order == "desc" else 1
    total = await db.diary_entries.count_documents(query)
    entries = await db.diary_entries.find(query, {"_id": 0}).sort(sort_by, sort_direction).to_list(1000)
    
    return DiaryListResponse(entries=[DiaryEntryResponse(**e) for e in entries], total=total)


@router.get("/projects/{project_id}/diary/{entry_id}", response_model=DiaryEntryResponse)
async def get_diary_entry(
    project_id: str,
    entry_id: str,
    current_user: dict = Depends(get_current_user)
):
    await verify_project_access(project_id, current_user["id"])
    
    entry = await db.diary_entries.find_one({"id": entry_id, "project_id": project_id}, {"_id": 0})
    if not entry:
        raise HTTPException(status_code=404, detail="Diary entry not found")
    
    return DiaryEntryResponse(**entry)


@router.put("/projects/{project_id}/diary/{entry_id}", response_model=DiaryEntryResponse)
async def update_diary_entry(
    project_id: str,
    entry_id: str,
    data: DiaryEntryUpdate,
    current_user: dict = Depends(get_current_user)
):
    await verify_project_access(project_id, current_user["id"])
    
    entry = await db.diary_entries.find_one({"id": entry_id, "project_id": project_id})
    if not entry:
        raise HTTPException(status_code=404, detail="Diary entry not found")
    
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.diary_entries.update_one({"id": entry_id}, {"$set": update_data})
    updated = await db.diary_entries.find_one({"id": entry_id}, {"_id": 0})
    return DiaryEntryResponse(**updated)


@router.delete("/projects/{project_id}/diary/{entry_id}", response_model=MessageResponse)
async def delete_diary_entry(
    project_id: str,
    entry_id: str,
    current_user: dict = Depends(get_current_user)
):
    await verify_project_access(project_id, current_user["id"])
    
    result = await db.diary_entries.delete_one({"id": entry_id, "project_id": project_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Diary entry not found")
    
    return MessageResponse(message="Diary entry deleted")
