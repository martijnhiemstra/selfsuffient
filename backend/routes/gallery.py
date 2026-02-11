"""Gallery routes."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import Optional
from datetime import datetime, timezone
import uuid

from config import db, UPLOADS_DIR, MAX_UPLOAD_SIZE, MAX_UPLOAD_SIZE_MB
from models import (
    GalleryFolderCreate, GalleryFolderUpdate, GalleryFolderResponse,
    GalleryImageResponse, GalleryListResponse, MessageResponse
)
from services import get_current_user, verify_project_access

router = APIRouter()


@router.post("/projects/{project_id}/gallery/folders", response_model=GalleryFolderResponse)
async def create_gallery_folder(
    project_id: str,
    data: GalleryFolderCreate,
    current_user: dict = Depends(get_current_user)
):
    await verify_project_access(project_id, current_user["id"])
    
    if data.parent_id:
        parent = await db.gallery_folders.find_one({"id": data.parent_id, "project_id": project_id})
        if not parent:
            raise HTTPException(status_code=404, detail="Parent folder not found")
    
    folder_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    folder_doc = {
        "id": folder_id,
        "project_id": project_id,
        "name": data.name,
        "parent_id": data.parent_id,
        "is_public": data.is_public,
        "created_at": now,
        "updated_at": now
    }
    
    await db.gallery_folders.insert_one(folder_doc)
    return GalleryFolderResponse(**{k: v for k, v in folder_doc.items() if k != "_id"})


@router.get("/projects/{project_id}/gallery", response_model=GalleryListResponse)
async def list_gallery_contents(
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
    image_query = {"project_id": project_id, "folder_id": folder_id}
    
    if search:
        folder_query["name"] = {"$regex": search, "$options": "i"}
        image_query["filename"] = {"$regex": search, "$options": "i"}
    
    folders = await db.gallery_folders.find(folder_query, {"_id": 0}).sort(sort_by, sort_direction).to_list(1000)
    images = await db.gallery_images.find(image_query, {"_id": 0}).sort(sort_by, sort_direction).to_list(1000)
    
    return GalleryListResponse(
        folders=[GalleryFolderResponse(**f) for f in folders],
        images=[GalleryImageResponse(**i) for i in images]
    )


@router.put("/projects/{project_id}/gallery/folders/{folder_id}", response_model=GalleryFolderResponse)
async def update_gallery_folder(
    project_id: str,
    folder_id: str,
    data: GalleryFolderUpdate,
    current_user: dict = Depends(get_current_user)
):
    await verify_project_access(project_id, current_user["id"])
    
    folder = await db.gallery_folders.find_one({"id": folder_id, "project_id": project_id})
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.gallery_folders.update_one({"id": folder_id}, {"$set": update_data})
    updated = await db.gallery_folders.find_one({"id": folder_id}, {"_id": 0})
    return GalleryFolderResponse(**updated)


@router.delete("/projects/{project_id}/gallery/folders/{folder_id}", response_model=MessageResponse)
async def delete_gallery_folder(
    project_id: str,
    folder_id: str,
    current_user: dict = Depends(get_current_user)
):
    await verify_project_access(project_id, current_user["id"])
    
    async def delete_folder_recursive(fid: str):
        subfolders = await db.gallery_folders.find({"parent_id": fid}).to_list(1000)
        for subfolder in subfolders:
            await delete_folder_recursive(subfolder["id"])
        
        images = await db.gallery_images.find({"folder_id": fid}).to_list(1000)
        for img in images:
            img_path = UPLOADS_DIR / img["url"].split("/uploads/")[-1]
            if img_path.exists():
                img_path.unlink()
        await db.gallery_images.delete_many({"folder_id": fid})
        await db.gallery_folders.delete_one({"id": fid})
    
    await delete_folder_recursive(folder_id)
    return MessageResponse(message="Folder and contents deleted")


@router.post("/projects/{project_id}/gallery/images", response_model=GalleryImageResponse)
async def upload_gallery_image(
    project_id: str,
    file: UploadFile = File(...),
    folder_id: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    await verify_project_access(project_id, current_user["id"])
    
    if folder_id:
        folder = await db.gallery_folders.find_one({"id": folder_id, "project_id": project_id})
        if not folder:
            raise HTTPException(status_code=404, detail="Folder not found")
    
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    # Check file size
    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413, 
            detail=f"File too large. Maximum size is {MAX_UPLOAD_SIZE_MB}MB"
        )
    
    image_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    gallery_dir = UPLOADS_DIR / "gallery" / project_id
    gallery_dir.mkdir(parents=True, exist_ok=True)
    
    file_ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{image_id}.{file_ext}"
    file_path = gallery_dir / filename
    
    # content already read for size check
    with open(file_path, "wb") as f:
        f.write(content)
    
    image_doc = {
        "id": image_id,
        "project_id": project_id,
        "folder_id": folder_id,
        "filename": file.filename,
        "url": f"/uploads/gallery/{project_id}/{filename}",
        "created_at": now
    }
    
    await db.gallery_images.insert_one(image_doc)
    return GalleryImageResponse(**{k: v for k, v in image_doc.items() if k != "_id"})


@router.delete("/projects/{project_id}/gallery/images/{image_id}", response_model=MessageResponse)
async def delete_gallery_image(
    project_id: str,
    image_id: str,
    current_user: dict = Depends(get_current_user)
):
    await verify_project_access(project_id, current_user["id"])
    
    image = await db.gallery_images.find_one({"id": image_id, "project_id": project_id})
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    img_path = UPLOADS_DIR / image["url"].split("/uploads/")[-1]
    if img_path.exists():
        img_path.unlink()
    
    await db.gallery_images.delete_one({"id": image_id})
    return MessageResponse(message="Image deleted")


# Gallery breadcrumb / path endpoint
@router.get("/projects/{project_id}/gallery/folders/{folder_id}/path")
async def get_gallery_folder_path(
    project_id: str,
    folder_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get the full path of a folder for breadcrumb navigation"""
    await verify_project_access(project_id, current_user["id"])
    
    path = []
    current_folder_id = folder_id
    
    while current_folder_id:
        folder = await db.gallery_folders.find_one(
            {"id": current_folder_id, "project_id": project_id},
            {"_id": 0}
        )
        if not folder:
            break
        path.insert(0, {"id": folder["id"], "name": folder["name"]})
        current_folder_id = folder.get("parent_id")
    
    return {"path": path}
