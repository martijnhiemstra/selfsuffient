"""Admin routes."""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime, timezone
import uuid

from config import db, logger
from models import UserCreate, UserResponse, MessageResponse
from services import hash_password, get_current_user

router = APIRouter()


@router.post("/users", response_model=UserResponse)
async def create_user(data: UserCreate, current_user: dict = Depends(get_current_user)):
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    existing = await db.users.find_one({"email": data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    user_doc = {
        "id": user_id,
        "email": data.email,
        "password": hash_password(data.password),
        "name": data.name,
        "is_admin": data.is_admin,
        "created_at": now,
        "updated_at": now
    }
    
    await db.users.insert_one(user_doc)
    
    return UserResponse(
        id=user_id,
        email=data.email,
        name=data.name,
        is_admin=data.is_admin,
        created_at=now
    )


@router.get("/users", response_model=List[UserResponse])
async def list_users(current_user: dict = Depends(get_current_user)):
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    users = await db.users.find({}, {"_id": 0, "password": 0}).to_list(1000)
    return [
        UserResponse(
            id=u["id"],
            email=u["email"],
            name=u["name"],
            is_admin=u.get("is_admin", False),
            created_at=u["created_at"]
        ) for u in users
    ]


@router.delete("/users/{user_id}", response_model=MessageResponse)
async def delete_user(user_id: str, current_user: dict = Depends(get_current_user)):
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if user_id == current_user["id"]:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    result = await db.users.delete_one({"id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return MessageResponse(message="User deleted successfully")


# Seed admin route
@router.post("/seed/admin", response_model=MessageResponse)
async def seed_admin():
    """Create initial admin user if none exists"""
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
    
    return MessageResponse(message="Admin user created successfully. Email: admin@selfsufficient.app, Password: admin123")
