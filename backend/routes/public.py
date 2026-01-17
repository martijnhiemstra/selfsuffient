"""Public routes."""
from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import datetime, timezone

from config import db
from models import (
    ProjectResponse, ProjectListResponse, BlogEntryResponse, BlogListResponse,
    LibraryFolderResponse, LibraryEntryResponse, LibraryListResponse,
    GalleryFolderResponse, GalleryImageResponse, PublicGalleryResponse,
    PublicUserProfileResponse
)

router = APIRouter()


@router.get("/users/{user_id}/profile", response_model=PublicUserProfileResponse)
async def get_public_user_profile(user_id: str):
    """Get a user's public profile with their public projects"""
    user = await db.users.find_one({"id": user_id}, {"_id": 0, "password": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    projects = await db.projects.find(
        {"user_id": user_id, "is_public": True},
        {"_id": 0}
    ).sort("created_at", -1).to_list(1000)
    
    return PublicUserProfileResponse(
        id=user["id"],
        name=user["name"],
        projects=[ProjectResponse(**p) for p in projects]
    )


@router.get("/projects", response_model=ProjectListResponse)
async def list_public_projects(
    search: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc"
):
    query = {"is_public": True}
    
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


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_public_project(project_id: str):
    project = await db.projects.find_one(
        {"id": project_id, "is_public": True},
        {"_id": 0}
    )
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    await db.project_views.update_one(
        {"project_id": project_id},
        {"$inc": {"views": 1}, "$set": {"last_viewed": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    
    return ProjectResponse(**project)


async def get_blog_images(blog_id: str) -> list:
    """Get all images for a blog entry"""
    images = await db.blog_images.find({"blog_id": blog_id}, {"_id": 0}).to_list(100)
    return images


async def build_blog_response(entry: dict) -> BlogEntryResponse:
    """Build a blog entry response with images"""
    from models import BlogImageResponse
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


# Public Blog routes
@router.get("/projects/{project_id}/blog", response_model=BlogListResponse)
async def list_public_blog_entries(
    project_id: str,
    search: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc"
):
    project = await db.projects.find_one({"id": project_id, "is_public": True})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    query = {"project_id": project_id, "is_public": True}
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
async def get_public_blog_entry(project_id: str, entry_id: str):
    project = await db.projects.find_one({"id": project_id, "is_public": True})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    entry = await db.blog_entries.find_one({"id": entry_id, "project_id": project_id, "is_public": True}, {"_id": 0})
    if not entry:
        raise HTTPException(status_code=404, detail="Blog entry not found")
    
    await db.blog_entries.update_one({"id": entry_id}, {"$inc": {"views": 1}})
    entry["views"] = entry.get("views", 0) + 1
    
    return await build_blog_response(entry)


# Public Library routes
@router.get("/projects/{project_id}/library", response_model=LibraryListResponse)
async def list_public_library_contents(
    project_id: str,
    folder_id: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc"
):
    project = await db.projects.find_one({"id": project_id, "is_public": True})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    sort_direction = -1 if sort_order == "desc" else 1
    
    folder_query = {"project_id": project_id, "parent_id": folder_id}
    entry_query = {"project_id": project_id, "folder_id": folder_id, "is_public": True}
    
    if search:
        folder_query["name"] = {"$regex": search, "$options": "i"}
        entry_query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    folders = await db.library_folders.find(folder_query, {"_id": 0}).sort(sort_by, sort_direction).to_list(1000)
    entries = await db.library_entries.find(entry_query, {"_id": 0}).sort(sort_by, sort_direction).to_list(1000)
    
    return LibraryListResponse(
        folders=[LibraryFolderResponse(**f) for f in folders],
        entries=[LibraryEntryResponse(**e) for e in entries]
    )


@router.get("/projects/{project_id}/library/entries/{entry_id}", response_model=LibraryEntryResponse)
async def get_public_library_entry(project_id: str, entry_id: str):
    project = await db.projects.find_one({"id": project_id, "is_public": True})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    entry = await db.library_entries.find_one({"id": entry_id, "project_id": project_id, "is_public": True}, {"_id": 0})
    if not entry:
        raise HTTPException(status_code=404, detail="Library entry not found")
    
    await db.library_entries.update_one({"id": entry_id}, {"$inc": {"views": 1}})
    entry["views"] = entry.get("views", 0) + 1
    
    return LibraryEntryResponse(**entry)


# Public Gallery routes
@router.get("/projects/{project_id}/gallery", response_model=PublicGalleryResponse)
async def list_public_gallery(
    project_id: str,
    folder_id: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc"
):
    """Get public gallery folders and their images for a public project"""
    project = await db.projects.find_one({"id": project_id, "is_public": True})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    sort_direction = -1 if sort_order == "desc" else 1
    
    folder_query = {"project_id": project_id, "is_public": True}
    if folder_id:
        folder_query["parent_id"] = folder_id
    else:
        folder_query["parent_id"] = None
    
    if search:
        folder_query["name"] = {"$regex": search, "$options": "i"}
    
    folders = await db.gallery_folders.find(folder_query, {"_id": 0}).sort(sort_by, sort_direction).to_list(1000)
    
    public_folder_ids = [f["id"] for f in await db.gallery_folders.find({"project_id": project_id, "is_public": True}, {"_id": 0, "id": 1}).to_list(1000)]
    
    image_query = {"project_id": project_id}
    if folder_id:
        if folder_id not in public_folder_ids:
            return PublicGalleryResponse(folders=[], images=[])
        image_query["folder_id"] = folder_id
    else:
        image_query["$or"] = [
            {"folder_id": {"$in": public_folder_ids}},
            {"folder_id": None}
        ]
    
    if search:
        image_query["filename"] = {"$regex": search, "$options": "i"}
    
    images = await db.gallery_images.find(image_query, {"_id": 0}).sort(sort_by, sort_direction).to_list(1000)
    
    return PublicGalleryResponse(
        folders=[GalleryFolderResponse(**{**f, "is_public": f.get("is_public", False)}) for f in folders],
        images=[GalleryImageResponse(**i) for i in images]
    )
