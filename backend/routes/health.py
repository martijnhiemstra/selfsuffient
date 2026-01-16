"""Health check routes."""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from datetime import datetime, timezone
from pathlib import Path

from config import db, APP_NAME, UPLOADS_DIR

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": APP_NAME,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/files/{file_path:path}")
async def serve_file(file_path: str):
    """Serve uploaded files with proper CORS headers"""
    full_path = UPLOADS_DIR / file_path
    
    if not full_path.exists() or not full_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Security check - ensure path is within uploads directory
    try:
        full_path.resolve().relative_to(UPLOADS_DIR.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")
    
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
