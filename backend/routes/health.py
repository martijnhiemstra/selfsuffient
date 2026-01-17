"""Health check routes."""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import jwt

from config import db, APP_NAME, UPLOADS_DIR, JWT_SECRET, JWT_ALGORITHM

router = APIRouter()
security = HTTPBearer(auto_error=False)


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": APP_NAME,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Get current user if authenticated, None otherwise"""
    if not credentials:
        return None
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            return None
        user = await db.users.find_one({"id": user_id}, {"_id": 0, "password": 0})
        return user
    except:
        return None


async def check_gallery_image_access(file_path: str, user: Optional[dict]) -> bool:
    """
    Check if the user has access to a gallery image.
    Returns True if access is allowed, False otherwise.
    """
    # Parse the file path to extract project_id and check if it's a gallery image
    # Path format: gallery/{project_id}/{image_id}.{ext}
    parts = file_path.split('/')
    
    if len(parts) < 2 or parts[0] != 'gallery':
        # Not a gallery image, allow access (project images, etc.)
        return True
    
    project_id = parts[1]
    
    # Find the image in the database
    image_filename = parts[-1] if len(parts) > 2 else None
    if not image_filename:
        return True
    
    # Get image id from filename (format: {uuid}.{ext})
    image_id = image_filename.rsplit('.', 1)[0] if '.' in image_filename else image_filename
    
    # Find the image
    image = await db.gallery_images.find_one({"id": image_id, "project_id": project_id})
    if not image:
        # Image not found in DB, might be legacy - allow access
        return True
    
    # Get the project
    project = await db.projects.find_one({"id": project_id})
    if not project:
        return False
    
    # If project is public, we need to check folder permissions
    folder_id = image.get("folder_id")
    
    if folder_id:
        # Image is in a folder - check if folder is public
        folder = await db.gallery_folders.find_one({"id": folder_id, "project_id": project_id})
        if folder:
            if folder.get("is_public", False):
                # Folder is public - allow access
                return True
            else:
                # Folder is private - only owner can access
                if not user:
                    return False
                return project.get("user_id") == user.get("id")
    else:
        # Image is in root of gallery
        if project.get("is_public", False):
            # Public project, root images are accessible
            return True
        else:
            # Private project - only owner can access
            if not user:
                return False
            return project.get("user_id") == user.get("id")
    
    # Default: check if user is owner
    if not user:
        return False
    return project.get("user_id") == user.get("id")


@router.get("/files/{file_path:path}")
async def serve_file(
    file_path: str,
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """Serve uploaded files with access control for private gallery images"""
    full_path = UPLOADS_DIR / file_path
    
    if not full_path.exists() or not full_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Security check - ensure path is within uploads directory
    try:
        full_path.resolve().relative_to(UPLOADS_DIR.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check gallery image access permissions
    if file_path.startswith("gallery/"):
        has_access = await check_gallery_image_access(file_path, current_user)
        if not has_access:
            raise HTTPException(status_code=403, detail="Access denied - this image is in a private folder")
    
    return FileResponse(
        full_path,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Cross-Origin-Resource-Policy": "cross-origin"
        }
    )


@router.get("/seed/admin")
async def seed_admin_get():
    """Alternative seed admin route (GET method for easy testing)"""
    import uuid
    from services import hash_password
    from config import logger
    
    admin_exists = await db.users.find_one({"is_admin": True})
    if admin_exists:
        raise HTTPException(status_code=400, detail="Admin user already exists")
    
    admin_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    admin_doc = {
        "id": admin_id,
        "email": "admin@selfsufficient.app",
        "password": hash_password("admin123"),
        "name": "Admin",
        "is_admin": True,
        "created_at": now,
        "updated_at": now
    }
    
    await db.users.insert_one(admin_doc)
    logger.info("Admin user created: admin@selfsufficient.app / admin123")
    
    return {"message": "Admin user created successfully. Email: admin@selfsufficient.app, Password: admin123"}
