"""Library routes."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import Optional, List
from datetime import datetime, timezone
from pathlib import Path
import uuid
import os

from config import db
from models import (
    LibraryFolderCreate, LibraryFolderUpdate, LibraryFolderResponse,
    LibraryEntryCreate, LibraryEntryUpdate, LibraryEntryResponse,
    LibraryImageResponse, LibraryListResponse, MessageResponse
)
from services import get_current_user, verify_project_access

router = APIRouter()

UPLOADS_DIR = Path("uploads")
MAX_UPLOAD_SIZE_MB = int(os.environ.get("MAX_UPLOAD_SIZE_MB", "5"))
MAX_UPLOAD_SIZE = MAX_UPLOAD_SIZE_MB * 1024 * 1024


async def get_entry_images(entry_id: str) -> List[dict]:
    images = await db.library_images.find({"entry_id": entry_id}, {"_id": 0}).to_list(100)
    return images


async def build_entry_response(entry: dict) -> LibraryEntryResponse:
    images = await get_entry_images(entry["id"])
    return LibraryEntryResponse(
        **{k: v for k, v in entry.items() if k != "_id"},
        images=[LibraryImageResponse(**img) for img in images]
    )


@router.post("/projects/{project_id}/library/folders", response_model=LibraryFolderResponse)
async def create_library_folder(
    project_id: str,
    data: LibraryFolderCreate,
    current_user: dict = Depends(get_current_user)
):
    await verify_project_access(project_id, current_user["id"])
    
    if data.parent_id:
        parent = await db.library_folders.find_one({"id": data.parent_id, "project_id": project_id})
        if not parent:
            raise HTTPException(status_code=404, detail="Parent folder not found")
    
    folder_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    folder_doc = {
        "id": folder_id,
        "project_id": project_id,
        "name": data.name,
        "parent_id": data.parent_id,
        "created_at": now,
        "updated_at": now
    }
    
    await db.library_folders.insert_one(folder_doc)
    return LibraryFolderResponse(**{k: v for k, v in folder_doc.items() if k != "_id"})


@router.get("/projects/{project_id}/library", response_model=LibraryListResponse)
async def list_library_contents(
    project_id: str,
    folder_id: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    current_user: dict = Depends(get_current_user)
):
    await verify_project_access(project_id, current_user["id"])
    
    sort_direction = -1 if sort_order == "desc" else 1
    
    folder_query = {"project_id": project_id, "parent_id": folder_id}
    entry_query = {"project_id": project_id, "folder_id": folder_id}
    
    if search:
        folder_query["name"] = {"$regex": search, "$options": "i"}
        entry_query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    folders = await db.library_folders.find(folder_query, {"_id": 0}).sort(sort_by, sort_direction).to_list(1000)
    entries = await db.library_entries.find(entry_query, {"_id": 0}).sort(sort_by, sort_direction).to_list(1000)
    
    entry_responses = []
    for e in entries:
        entry_responses.append(await build_entry_response(e))
    
    return LibraryListResponse(
        folders=[LibraryFolderResponse(**f) for f in folders],
        entries=entry_responses
    )


@router.put("/projects/{project_id}/library/folders/{folder_id}", response_model=LibraryFolderResponse)
async def update_library_folder(
    project_id: str,
    folder_id: str,
    data: LibraryFolderUpdate,
    current_user: dict = Depends(get_current_user)
):
    await verify_project_access(project_id, current_user["id"])
    
    folder = await db.library_folders.find_one({"id": folder_id, "project_id": project_id})
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.library_folders.update_one({"id": folder_id}, {"$set": update_data})
    updated = await db.library_folders.find_one({"id": folder_id}, {"_id": 0})
    return LibraryFolderResponse(**updated)


@router.delete("/projects/{project_id}/library/folders/{folder_id}", response_model=MessageResponse)
async def delete_library_folder(
    project_id: str,
    folder_id: str,
    current_user: dict = Depends(get_current_user)
):
    await verify_project_access(project_id, current_user["id"])
    
    async def delete_folder_recursive(fid: str):
        subfolders = await db.library_folders.find({"parent_id": fid}).to_list(1000)
        for subfolder in subfolders:
            await delete_folder_recursive(subfolder["id"])
        await db.library_entries.delete_many({"folder_id": fid})
        await db.library_folders.delete_one({"id": fid})
    
    await delete_folder_recursive(folder_id)
    return MessageResponse(message="Folder and contents deleted")


@router.post("/projects/{project_id}/library/entries", response_model=LibraryEntryResponse)
async def create_library_entry(
    project_id: str,
    data: LibraryEntryCreate,
    current_user: dict = Depends(get_current_user)
):
    await verify_project_access(project_id, current_user["id"])
    
    if data.folder_id:
        folder = await db.library_folders.find_one({"id": data.folder_id, "project_id": project_id})
        if not folder:
            raise HTTPException(status_code=404, detail="Folder not found")
    
    entry_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    entry_doc = {
        "id": entry_id,
        "project_id": project_id,
        "folder_id": data.folder_id,
        "title": data.title,
        "description": data.description,
        "is_public": data.is_public,
        "views": 0,
        "created_at": now,
        "updated_at": now
    }
    
    await db.library_entries.insert_one(entry_doc)
    return await build_entry_response({k: v for k, v in entry_doc.items() if k != "_id"})


@router.get("/projects/{project_id}/library/entries/{entry_id}", response_model=LibraryEntryResponse)
async def get_library_entry(
    project_id: str,
    entry_id: str,
    current_user: dict = Depends(get_current_user)
):
    await verify_project_access(project_id, current_user["id"])
    
    entry = await db.library_entries.find_one({"id": entry_id, "project_id": project_id}, {"_id": 0})
    if not entry:
        raise HTTPException(status_code=404, detail="Library entry not found")
    
    return await build_entry_response(entry)


@router.put("/projects/{project_id}/library/entries/{entry_id}", response_model=LibraryEntryResponse)
async def update_library_entry(
    project_id: str,
    entry_id: str,
    data: LibraryEntryUpdate,
    current_user: dict = Depends(get_current_user)
):
    await verify_project_access(project_id, current_user["id"])
    
    entry = await db.library_entries.find_one({"id": entry_id, "project_id": project_id})
    if not entry:
        raise HTTPException(status_code=404, detail="Library entry not found")
    
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.library_entries.update_one({"id": entry_id}, {"$set": update_data})
    updated = await db.library_entries.find_one({"id": entry_id}, {"_id": 0})
    return await build_entry_response(updated)


@router.delete("/projects/{project_id}/library/entries/{entry_id}", response_model=MessageResponse)
async def delete_library_entry(
    project_id: str,
    entry_id: str,
    current_user: dict = Depends(get_current_user)
):
    await verify_project_access(project_id, current_user["id"])
    
    result = await db.library_entries.delete_one({"id": entry_id, "project_id": project_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Library entry not found")
    
    # Delete associated images
    images = await db.library_images.find({"entry_id": entry_id}).to_list(100)
    for img in images:
        img_path = UPLOADS_DIR / img["url"].split("/uploads/")[-1]
        if img_path.exists():
            img_path.unlink()
    await db.library_images.delete_many({"entry_id": entry_id})
    
    return MessageResponse(message="Library entry deleted")


# Library breadcrumb / path endpoint
@router.get("/projects/{project_id}/library/folders/{folder_id}/path")
async def get_library_folder_path(
    project_id: str,
    folder_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get the full path of a folder for breadcrumb navigation"""
    await verify_project_access(project_id, current_user["id"])
    
    path = []
    current_folder_id = folder_id
    
    while current_folder_id:
        folder = await db.library_folders.find_one(
            {"id": current_folder_id, "project_id": project_id},
            {"_id": 0}
        )
        if not folder:
            break
        path.insert(0, {"id": folder["id"], "name": folder["name"]})
        current_folder_id = folder.get("parent_id")
    
    return {"path": path}


@router.post("/projects/{project_id}/library/entries/{entry_id}/images", response_model=LibraryImageResponse)
async def upload_library_image(
    project_id: str,
    entry_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload an image attachment to a library entry"""
    await verify_project_access(project_id, current_user["id"])

    entry = await db.library_entries.find_one({"id": entry_id, "project_id": project_id})
    if not entry:
        raise HTTPException(status_code=404, detail="Library entry not found")

    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Allowed: JPEG, PNG, GIF, WEBP")

    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail=f"File too large. Maximum size is {MAX_UPLOAD_SIZE_MB}MB")

    image_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    lib_dir = UPLOADS_DIR / "library" / project_id / entry_id
    lib_dir.mkdir(parents=True, exist_ok=True)

    file_ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{image_id}.{file_ext}"
    file_path = lib_dir / filename

    with open(file_path, "wb") as f:
        f.write(content)

    image_doc = {
        "id": image_id,
        "entry_id": entry_id,
        "project_id": project_id,
        "filename": file.filename,
        "url": f"/uploads/library/{project_id}/{entry_id}/{filename}",
        "created_at": now
    }

    await db.library_images.insert_one(image_doc)
    return LibraryImageResponse(**{k: v for k, v in image_doc.items() if k != "_id"})


@router.delete("/projects/{project_id}/library/entries/{entry_id}/images/{image_id}", response_model=MessageResponse)
async def delete_library_image(
    project_id: str,
    entry_id: str,
    image_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete an image from a library entry"""
    await verify_project_access(project_id, current_user["id"])

    image = await db.library_images.find_one({"id": image_id, "entry_id": entry_id, "project_id": project_id})
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    img_path = UPLOADS_DIR / image["url"].split("/uploads/")[-1]
    if img_path.exists():
        img_path.unlink()

    await db.library_images.delete_one({"id": image_id})
    return MessageResponse(message="Image deleted")
