"""Blog routes."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import Optional, List
from datetime import datetime, timezone
import uuid

from config import db, UPLOADS_DIR, MAX_UPLOAD_SIZE, MAX_UPLOAD_SIZE_MB
from models import BlogEntryCreate, BlogEntryUpdate, BlogEntryResponse, BlogListResponse, BlogImageResponse, MessageResponse
from services import get_current_user, verify_project_access

router = APIRouter()


async def get_blog_images(blog_id: str) -> List[dict]:
    """Get all images for a blog entry"""
    images = await db.blog_images.find({"blog_id": blog_id}, {"_id": 0}).to_list(100)
    return images


async def build_blog_response(entry: dict) -> BlogEntryResponse:
    """Build a blog entry response with images"""
    images = await get_blog_images(entry["id"])
    return BlogEntryResponse(
        id=entry["id"],
        project_id=entry["project_id"],
        title=entry["title"],
        description=entry["description"],
        is_public=entry.get("is_public", False),
        views=entry.get("views", 0),
        images=[BlogImageResponse(**img) for img in images],
        created_at=entry["created_at"],
        updated_at=entry["updated_at"]
    )


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
    return await build_blog_response(entry_doc)


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
    
    # Build responses with images
    responses = []
    for entry in entries:
        responses.append(await build_blog_response(entry))
    
    return BlogListResponse(entries=responses, total=total)


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
    
    return await build_blog_response(entry)


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
    return await build_blog_response(updated)


@router.delete("/projects/{project_id}/blog/{entry_id}", response_model=MessageResponse)
async def delete_blog_entry(
    project_id: str,
    entry_id: str,
    current_user: dict = Depends(get_current_user)
):
    await verify_project_access(project_id, current_user["id"])
    
    entry = await db.blog_entries.find_one({"id": entry_id, "project_id": project_id})
    if not entry:
        raise HTTPException(status_code=404, detail="Blog entry not found")
    
    # Delete associated images from disk
    images = await db.blog_images.find({"blog_id": entry_id}).to_list(100)
    for img in images:
        img_path = UPLOADS_DIR / img["url"].split("/uploads/")[-1]
        if img_path.exists():
            img_path.unlink()
    
    # Delete images from database
    await db.blog_images.delete_many({"blog_id": entry_id})
    
    # Delete the blog entry
    await db.blog_entries.delete_one({"id": entry_id})
    
    return MessageResponse(message="Blog entry deleted")


# Blog Image endpoints
@router.post("/projects/{project_id}/blog/{entry_id}/images", response_model=BlogImageResponse)
async def upload_blog_image(
    project_id: str,
    entry_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload an image attachment to a blog entry"""
    await verify_project_access(project_id, current_user["id"])
    
    # Verify blog entry exists
    entry = await db.blog_entries.find_one({"id": entry_id, "project_id": project_id})
    if not entry:
        raise HTTPException(status_code=404, detail="Blog entry not found")
    
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Allowed: JPEG, PNG, GIF, WEBP")
    
    # Check file size
    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413, 
            detail=f"File too large. Maximum size is {MAX_UPLOAD_SIZE_MB}MB"
        )
    
    image_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    # Create blog images directory
    blog_dir = UPLOADS_DIR / "blog" / project_id / entry_id
    blog_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    file_ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{image_id}.{file_ext}"
    file_path = blog_dir / filename
    
    # content already read for size check
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Save to database
    image_doc = {
        "id": image_id,
        "blog_id": entry_id,
        "project_id": project_id,
        "filename": file.filename,
        "url": f"/uploads/blog/{project_id}/{entry_id}/{filename}",
        "created_at": now
    }
    
    await db.blog_images.insert_one(image_doc)
    
    return BlogImageResponse(**{k: v for k, v in image_doc.items() if k != "_id"})


@router.delete("/projects/{project_id}/blog/{entry_id}/images/{image_id}", response_model=MessageResponse)
async def delete_blog_image(
    project_id: str,
    entry_id: str,
    image_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete an image attachment from a blog entry"""
    await verify_project_access(project_id, current_user["id"])
    
    image = await db.blog_images.find_one({
        "id": image_id,
        "blog_id": entry_id,
        "project_id": project_id
    })
    
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Delete file from disk
    img_path = UPLOADS_DIR / image["url"].split("/uploads/")[-1]
    if img_path.exists():
        img_path.unlink()
    
    # Delete from database
    await db.blog_images.delete_one({"id": image_id})
    
    return MessageResponse(message="Image deleted")
