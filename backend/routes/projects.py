"""Project routes."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import Optional
from datetime import datetime, timezone
import uuid

from config import db, UPLOADS_DIR
from models import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse, MessageResponse
from services import get_current_user

router = APIRouter()


@router.post("", response_model=ProjectResponse)
async def create_project(data: ProjectCreate, current_user: dict = Depends(get_current_user)):
    project_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    project_doc = {
        "id": project_id,
        "user_id": current_user["id"],
        "name": data.name,
        "description": data.description,
        "image": None,
        "is_public": data.is_public,
        "created_at": now,
        "updated_at": now
    }
    
    await db.projects.insert_one(project_doc)
    
    return ProjectResponse(**{k: v for k, v in project_doc.items() if k != "_id"})


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    search: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    current_user: dict = Depends(get_current_user)
):
    query = {"user_id": current_user["id"]}
    
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    sort_direction = -1 if sort_order == "desc" else 1
    
    total = await db.projects.count_documents(query)
    projects = await db.projects.find(query, {"_id": 0}).sort(sort_by, sort_direction).to_list(1000)
    
    return ProjectListResponse(
        projects=[ProjectResponse(**p) for p in projects],
        total=total
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, current_user: dict = Depends(get_current_user)):
    project = await db.projects.find_one(
        {"id": project_id, "user_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return ProjectResponse(**project)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    data: ProjectUpdate,
    current_user: dict = Depends(get_current_user)
):
    project = await db.projects.find_one(
        {"id": project_id, "user_id": current_user["id"]}
    )
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.projects.update_one(
        {"id": project_id},
        {"$set": update_data}
    )
    
    updated = await db.projects.find_one({"id": project_id}, {"_id": 0})
    return ProjectResponse(**updated)


@router.delete("/{project_id}", response_model=MessageResponse)
async def delete_project(project_id: str, current_user: dict = Depends(get_current_user)):
    project = await db.projects.find_one(
        {"id": project_id, "user_id": current_user["id"]}
    )
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Delete project image if exists
    if project.get("image"):
        image_path = UPLOADS_DIR / project["image"].split("/uploads/")[-1]
        if image_path.exists():
            image_path.unlink()
    
    # Delete all related data
    await db.diary_entries.delete_many({"project_id": project_id})
    await db.gallery_folders.delete_many({"project_id": project_id})
    await db.gallery_images.delete_many({"project_id": project_id})
    await db.blog_entries.delete_many({"project_id": project_id})
    await db.library_folders.delete_many({"project_id": project_id})
    await db.library_entries.delete_many({"project_id": project_id})
    await db.tasks.delete_many({"project_id": project_id})
    await db.startup_tasks.delete_many({"project_id": project_id})
    await db.shutdown_tasks.delete_many({"project_id": project_id})
    
    await db.projects.delete_one({"id": project_id})
    
    return MessageResponse(message="Project deleted successfully")


@router.post("/{project_id}/image", response_model=ProjectResponse)
async def upload_project_image(
    project_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    project = await db.projects.find_one(
        {"id": project_id, "user_id": current_user["id"]}
    )
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Allowed: JPEG, PNG, GIF, WEBP")
    
    project_dir = UPLOADS_DIR / "projects" / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    
    if project.get("image"):
        old_path = UPLOADS_DIR / project["image"].split("/uploads/")[-1]
        if old_path.exists():
            old_path.unlink()
    
    file_ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"cover.{file_ext}"
    file_path = project_dir / filename
    
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    image_url = f"/uploads/projects/{project_id}/{filename}"
    await db.projects.update_one(
        {"id": project_id},
        {"$set": {"image": image_url, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    updated = await db.projects.find_one({"id": project_id}, {"_id": 0})
    return ProjectResponse(**updated)
