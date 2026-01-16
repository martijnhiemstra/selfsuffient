from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import jwt
import bcrypt
import secrets

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', secrets.token_hex(32))
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Create the main app
app = FastAPI(title="Self-Sufficient Lifestyle App")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer()

# Ensure uploads directory exists
UPLOADS_DIR = ROOT_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============ MODELS ============

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    is_admin: bool = False

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    is_admin: bool
    created_at: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class MessageResponse(BaseModel):
    message: str

# ============ PROJECT MODELS ============

class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=5000)
    is_public: bool = False

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    is_public: Optional[bool] = None

class ProjectResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: str
    image: Optional[str] = None
    is_public: bool
    created_at: str
    updated_at: str

class ProjectListResponse(BaseModel):
    projects: List[ProjectResponse]
    total: int

# ============ HELPER FUNCTIONS ============

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_token(user_id: str, email: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await db.users.find_one({"id": user_id}, {"_id": 0, "password": 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ============ AUTH ROUTES ============

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(data: UserLogin):
    user = await db.users.find_one({"email": data.email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(user["id"], user["email"])
    
    user_response = UserResponse(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        is_admin=user.get("is_admin", False),
        created_at=user["created_at"]
    )
    
    return TokenResponse(access_token=token, user=user_response)

@api_router.post("/auth/forgot-password", response_model=MessageResponse)
async def forgot_password(data: ForgotPasswordRequest):
    user = await db.users.find_one({"email": data.email}, {"_id": 0})
    if not user:
        # Return success even if user doesn't exist (security)
        return MessageResponse(message="If the email exists, a reset link has been sent")
    
    # Create reset token
    reset_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    
    await db.password_resets.insert_one({
        "id": str(uuid.uuid4()),
        "user_id": user["id"],
        "token": reset_token,
        "expires_at": expires_at.isoformat(),
        "used": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    # In a real app, send email here
    # For now, log the token (dev only)
    logger.info(f"Password reset token for {data.email}: {reset_token}")
    
    return MessageResponse(message="If the email exists, a reset link has been sent")

@api_router.post("/auth/reset-password", response_model=MessageResponse)
async def reset_password(data: ResetPasswordRequest):
    reset_record = await db.password_resets.find_one({
        "token": data.token,
        "used": False
    }, {"_id": 0})
    
    if not reset_record:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    expires_at = datetime.fromisoformat(reset_record["expires_at"])
    if datetime.now(timezone.utc) > expires_at:
        raise HTTPException(status_code=400, detail="Reset token has expired")
    
    # Update password
    hashed_password = hash_password(data.new_password)
    await db.users.update_one(
        {"id": reset_record["user_id"]},
        {"$set": {"password": hashed_password, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    # Mark token as used
    await db.password_resets.update_one(
        {"token": data.token},
        {"$set": {"used": True}}
    )
    
    return MessageResponse(message="Password reset successfully")

@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        name=current_user["name"],
        is_admin=current_user.get("is_admin", False),
        created_at=current_user["created_at"]
    )

@api_router.post("/auth/change-password", response_model=MessageResponse)
async def change_password(data: ChangePasswordRequest, current_user: dict = Depends(get_current_user)):
    # Get user with password
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    
    if not verify_password(data.current_password, user["password"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    hashed_password = hash_password(data.new_password)
    await db.users.update_one(
        {"id": current_user["id"]},
        {"$set": {"password": hashed_password, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return MessageResponse(message="Password changed successfully")

# ============ ADMIN ROUTES ============

@api_router.post("/admin/users", response_model=UserResponse)
async def create_user(data: UserCreate, current_user: dict = Depends(get_current_user)):
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Check if email already exists
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

@api_router.get("/admin/users", response_model=List[UserResponse])
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

@api_router.delete("/admin/users/{user_id}", response_model=MessageResponse)
async def delete_user(user_id: str, current_user: dict = Depends(get_current_user)):
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if user_id == current_user["id"]:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    result = await db.users.delete_one({"id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return MessageResponse(message="User deleted successfully")

# ============ SEED ADMIN ROUTE ============

@api_router.post("/seed/admin", response_model=MessageResponse)
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

# ============ PROJECT ROUTES ============

@api_router.post("/projects", response_model=ProjectResponse)
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

@api_router.get("/projects", response_model=ProjectListResponse)
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

@api_router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, current_user: dict = Depends(get_current_user)):
    project = await db.projects.find_one(
        {"id": project_id, "user_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return ProjectResponse(**project)

@api_router.put("/projects/{project_id}", response_model=ProjectResponse)
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

@api_router.delete("/projects/{project_id}", response_model=MessageResponse)
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

@api_router.post("/projects/{project_id}/image", response_model=ProjectResponse)
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
    
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Allowed: JPEG, PNG, GIF, WEBP")
    
    # Create project images directory
    project_dir = UPLOADS_DIR / "projects" / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    
    # Delete old image if exists
    if project.get("image"):
        old_path = UPLOADS_DIR / project["image"].split("/uploads/")[-1]
        if old_path.exists():
            old_path.unlink()
    
    # Save new image
    file_ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"cover.{file_ext}"
    file_path = project_dir / filename
    
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Update project with image URL
    image_url = f"/uploads/projects/{project_id}/{filename}"
    await db.projects.update_one(
        {"id": project_id},
        {"$set": {"image": image_url, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    updated = await db.projects.find_one({"id": project_id}, {"_id": 0})
    return ProjectResponse(**updated)

# ============ PUBLIC ROUTES ============

@api_router.get("/public/projects", response_model=ProjectListResponse)
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

@api_router.get("/public/projects/{project_id}", response_model=ProjectResponse)
async def get_public_project(project_id: str):
    project = await db.projects.find_one(
        {"id": project_id, "is_public": True},
        {"_id": 0}
    )
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Increment view count
    await db.project_views.update_one(
        {"project_id": project_id},
        {"$inc": {"views": 1}, "$set": {"last_viewed": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    
    return ProjectResponse(**project)

# ============ HEALTH CHECK ============

@api_router.get("/")
async def root():
    return {"message": "Self-Sufficient Lifestyle API", "status": "healthy"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

# Include the router in the main app
app.include_router(api_router)

# Mount static files for uploads
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Create indexes
    await db.users.create_index("email", unique=True)
    await db.users.create_index("id", unique=True)
    await db.password_resets.create_index("token")
    await db.password_resets.create_index("user_id")
    logger.info("Database indexes created")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
