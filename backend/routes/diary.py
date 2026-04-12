"""Diary routes."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import Optional, List
from datetime import datetime, timezone
import uuid

from config import db, UPLOADS_DIR, MAX_UPLOAD_SIZE, MAX_UPLOAD_SIZE_MB
from models import DiaryEntryCreate, DiaryEntryUpdate, DiaryEntryResponse, DiaryListResponse, DiaryImageResponse, MessageResponse
from services import get_current_user, verify_project_access

router = APIRouter()


async def get_diary_images(diary_id: str) -> List[dict]:
    """Get all images for a diary entry"""
    images = await db.diary_images.find({"diary_id": diary_id}, {"_id": 0}).to_list(100)
    return images


async def build_diary_response(entry: dict) -> DiaryEntryResponse:
    """Build a diary entry response with images"""
    images = await get_diary_images(entry["id"])
    return DiaryEntryResponse(
        **{k: v for k, v in entry.items() if k != "_id"},
        images=[DiaryImageResponse(**img) for img in images]
    )


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
    return await build_diary_response({k: v for k, v in entry_doc.items() if k != "_id"})


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
    
    responses = []
    for entry in entries:
        responses.append(await build_diary_response(entry))
    
    return DiaryListResponse(entries=responses, total=total)


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
    
    return await build_diary_response(entry)


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
    return await build_diary_response(updated)


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
    
    # Delete associated images from disk
    images = await db.diary_images.find({"diary_id": entry_id}).to_list(100)
    for img in images:
        img_path = UPLOADS_DIR / img["url"].split("/uploads/")[-1]
        if img_path.exists():
            img_path.unlink()
    await db.diary_images.delete_many({"diary_id": entry_id})
    
    return MessageResponse(message="Diary entry deleted")


# Diary Image endpoints
@router.post("/projects/{project_id}/diary/{entry_id}/images", response_model=DiaryImageResponse)
async def upload_diary_image(
    project_id: str,
    entry_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload an image attachment to a diary entry"""
    await verify_project_access(project_id, current_user["id"])
    
    entry = await db.diary_entries.find_one({"id": entry_id, "project_id": project_id})
    if not entry:
        raise HTTPException(status_code=404, detail="Diary entry not found")
    
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Allowed: JPEG, PNG, GIF, WEBP")
    
    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail=f"File too large. Maximum size is {MAX_UPLOAD_SIZE_MB}MB")
    
    image_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    diary_dir = UPLOADS_DIR / "diary" / project_id / entry_id
    diary_dir.mkdir(parents=True, exist_ok=True)
    
    file_ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{image_id}.{file_ext}"
    file_path = diary_dir / filename
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    image_doc = {
        "id": image_id,
        "diary_id": entry_id,
        "project_id": project_id,
        "filename": file.filename,
        "url": f"/uploads/diary/{project_id}/{entry_id}/{filename}",
        "created_at": now
    }
    
    await db.diary_images.insert_one(image_doc)
    return DiaryImageResponse(**{k: v for k, v in image_doc.items() if k != "_id"})


@router.delete("/projects/{project_id}/diary/{entry_id}/images/{image_id}", response_model=MessageResponse)
async def delete_diary_image(
    project_id: str,
    entry_id: str,
    image_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete an image attachment from a diary entry"""
    await verify_project_access(project_id, current_user["id"])
    
    image = await db.diary_images.find_one({
        "id": image_id,
        "diary_id": entry_id,
        "project_id": project_id
    })
    
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    img_path = UPLOADS_DIR / image["url"].split("/uploads/")[-1]
    if img_path.exists():
        img_path.unlink()
    
    await db.diary_images.delete_one({"id": image_id})
    return MessageResponse(message="Image deleted")
