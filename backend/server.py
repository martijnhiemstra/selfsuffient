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
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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

# Email Configuration (SMTP with SSL)
SMTP_HOST = os.environ.get('SMTP_HOST', '')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '465'))
SMTP_USER = os.environ.get('SMTP_USER', '')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
SMTP_FROM_EMAIL = os.environ.get('SMTP_FROM_EMAIL', '')
SMTP_FROM_NAME = os.environ.get('SMTP_FROM_NAME', 'Self-Sufficient Life')

# App Configuration
APP_NAME = os.environ.get('APP_NAME', 'Self-Sufficient Life')
APP_URL = os.environ.get('APP_URL', 'http://localhost:3000')

# Create the main app
app = FastAPI(title=APP_NAME)

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
    daily_reminders: bool = False

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    is_admin: bool
    daily_reminders: bool = False
    created_at: str

class UserUpdateSettings(BaseModel):
    daily_reminders: Optional[bool] = None

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

# ============ DIARY MODELS ============

class DiaryEntryCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    story: str = Field(default="", max_length=10000)
    entry_datetime: Optional[str] = None

class DiaryEntryUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    story: Optional[str] = Field(None, max_length=10000)
    entry_datetime: Optional[str] = None

class DiaryEntryResponse(BaseModel):
    id: str
    project_id: str
    title: str
    story: str
    entry_datetime: str
    created_at: str
    updated_at: str

class DiaryListResponse(BaseModel):
    entries: List[DiaryEntryResponse]
    total: int

# ============ GALLERY MODELS ============

class GalleryFolderCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    parent_id: Optional[str] = None
    is_public: bool = False

class GalleryFolderUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    parent_id: Optional[str] = None
    is_public: Optional[bool] = None

class GalleryFolderResponse(BaseModel):
    id: str
    project_id: str
    name: str
    parent_id: Optional[str] = None
    is_public: bool = False
    created_at: str
    updated_at: str

class GalleryImageResponse(BaseModel):
    id: str
    project_id: str
    folder_id: Optional[str] = None
    filename: str
    url: str
    created_at: str

class GalleryListResponse(BaseModel):
    folders: List[GalleryFolderResponse]
    images: List[GalleryImageResponse]

# ============ BLOG MODELS ============

class BlogEntryCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=10000)
    is_public: bool = False

class BlogEntryUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=10000)
    is_public: Optional[bool] = None

class BlogEntryResponse(BaseModel):
    id: str
    project_id: str
    title: str
    description: str
    is_public: bool
    views: int = 0
    created_at: str
    updated_at: str

class BlogListResponse(BaseModel):
    entries: List[BlogEntryResponse]
    total: int

# ============ LIBRARY MODELS ============

class LibraryFolderCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    parent_id: Optional[str] = None

class LibraryFolderUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    parent_id: Optional[str] = None

class LibraryFolderResponse(BaseModel):
    id: str
    project_id: str
    name: str
    parent_id: Optional[str] = None
    created_at: str
    updated_at: str

class LibraryEntryCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=10000)
    folder_id: Optional[str] = None
    is_public: bool = False

class LibraryEntryUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=10000)
    folder_id: Optional[str] = None
    is_public: Optional[bool] = None

class LibraryEntryResponse(BaseModel):
    id: str
    project_id: str
    folder_id: Optional[str] = None
    title: str
    description: str
    is_public: bool
    views: int = 0
    created_at: str
    updated_at: str

class LibraryListResponse(BaseModel):
    folders: List[LibraryFolderResponse]
    entries: List[LibraryEntryResponse]

# ============ TASK MODELS ============

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=5000)
    task_datetime: str
    is_all_day: bool = False
    recurrence: Optional[str] = None  # none, daily, weekly, monthly, yearly

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    task_datetime: Optional[str] = None
    is_all_day: Optional[bool] = None
    recurrence: Optional[str] = None

class TaskResponse(BaseModel):
    id: str
    project_id: str
    title: str
    description: str
    task_datetime: str
    is_all_day: bool
    recurrence: Optional[str] = None
    created_at: str
    updated_at: str

class TaskListResponse(BaseModel):
    tasks: List[TaskResponse]
    total: int

# ============ ROUTINE MODELS ============

class RoutineTaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)
    order: int = 0

class RoutineTaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    order: Optional[int] = None

class RoutineTaskResponse(BaseModel):
    id: str
    project_id: str
    routine_type: str  # startup or shutdown
    title: str
    description: str
    order: int
    created_at: str

class RoutineCompletionResponse(BaseModel):
    id: str
    task_id: str
    completed_date: str
    created_at: str

class RoutineListResponse(BaseModel):
    tasks: List[RoutineTaskResponse]
    completions_today: List[str]  # list of task_ids completed today

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

def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """Send email via SMTP with SSL on port 465"""
    if not all([SMTP_HOST, SMTP_USER, SMTP_PASSWORD, SMTP_FROM_EMAIL]):
        logger.warning("SMTP not configured, email not sent")
        return False
    
    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
        message["To"] = to_email
        
        # Create HTML part
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)
        
        # Create SSL context and send
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_FROM_EMAIL, to_email, message.as_string())
        
        logger.info(f"Email sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False

def get_password_reset_email_html(reset_url: str, user_name: str) -> str:
    """Generate password reset email HTML"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #2d5a3d 0%, #4a7c59 100%); color: white; padding: 30px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 24px; }}
            .content {{ padding: 30px; }}
            .button {{ display: inline-block; background: #2d5a3d; color: white; text-decoration: none; padding: 14px 28px; border-radius: 25px; font-weight: bold; margin: 20px 0; }}
            .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; border-top: 1px solid #eee; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{APP_NAME}</h1>
            </div>
            <div class="content">
                <p>Hello {user_name},</p>
                <p>We received a request to reset your password. Click the button below to create a new password:</p>
                <p style="text-align: center;">
                    <a href="{reset_url}" class="button">Reset Password</a>
                </p>
                <p>This link will expire in 1 hour.</p>
                <p>If you didn't request this, you can safely ignore this email.</p>
                <p>Best regards,<br>The {APP_NAME} Team</p>
            </div>
            <div class="footer">
                <p>This is an automated message from {APP_NAME}.</p>
            </div>
        </div>
    </body>
    </html>
    """

def get_daily_reminder_email_html(user_name: str, startup_tasks: list, daily_tasks: list, shutdown_tasks: list) -> str:
    """Generate daily reminder email HTML"""
    
    def format_task_list(tasks: list, section_name: str, icon: str) -> str:
        if not tasks:
            return ""
        items = "".join([f'<li style="padding: 8px 0; border-bottom: 1px solid #eee;">{t["title"]}</li>' for t in tasks])
        return f"""
        <div style="margin: 20px 0;">
            <h3 style="color: #2d5a3d; margin-bottom: 10px;">{icon} {section_name}</h3>
            <ul style="list-style: none; padding: 0; margin: 0;">{items}</ul>
        </div>
        """
    
    startup_html = format_task_list(startup_tasks, "Start of Day Items", "🌅")
    daily_html = format_task_list(daily_tasks, "Today's Tasks", "📋")
    shutdown_html = format_task_list(shutdown_tasks, "End of Day Items", "🌙")
    
    today = datetime.now().strftime("%A, %B %d, %Y")
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #2d5a3d 0%, #4a7c59 100%); color: white; padding: 30px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 24px; }}
            .header p {{ margin: 10px 0 0; opacity: 0.9; }}
            .content {{ padding: 30px; }}
            .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; border-top: 1px solid #eee; }}
            .button {{ display: inline-block; background: #2d5a3d; color: white; text-decoration: none; padding: 12px 24px; border-radius: 25px; font-weight: bold; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Good Morning, {user_name}!</h1>
                <p>{today}</p>
            </div>
            <div class="content">
                <p>Here's your daily task summary to help you stay on track:</p>
                {startup_html}
                {daily_html}
                {shutdown_html}
                {f'<p style="text-align: center; color: #666; margin-top: 30px;">No tasks scheduled for today. Enjoy your day!</p>' if not (startup_tasks or daily_tasks or shutdown_tasks) else ''}
                <p style="text-align: center; margin-top: 30px;">
                    <a href="{APP_URL}/dashboard" class="button">Open Dashboard</a>
                </p>
            </div>
            <div class="footer">
                <p>You're receiving this because you enabled daily reminders.</p>
                <p>Manage your preferences in <a href="{APP_URL}/settings">Settings</a>.</p>
            </div>
        </div>
    </body>
    </html>
    """

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
        daily_reminders=user.get("daily_reminders", False),
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
    
    # Send password reset email
    reset_url = f"{APP_URL}/reset-password?token={reset_token}"
    email_html = get_password_reset_email_html(reset_url, user.get("name", "User"))
    email_sent = send_email(data.email, f"Reset Your {APP_NAME} Password", email_html)
    
    if not email_sent:
        # Log token for development if email not configured
        logger.info(f"Password reset token for {data.email}: {reset_token}")
        logger.info(f"Reset URL: {reset_url}")
    
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
        daily_reminders=current_user.get("daily_reminders", False),
        created_at=current_user["created_at"]
    )

@api_router.put("/auth/settings", response_model=UserResponse)
async def update_user_settings(data: UserUpdateSettings, current_user: dict = Depends(get_current_user)):
    """Update user settings like daily reminders"""
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if update_data:
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        await db.users.update_one({"id": current_user["id"]}, {"$set": update_data})
    
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0, "password": 0})
    return UserResponse(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        is_admin=user.get("is_admin", False),
        daily_reminders=user.get("daily_reminders", False),
        created_at=user["created_at"]
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

class PublicUserProfileResponse(BaseModel):
    id: str
    name: str
    projects: List[ProjectResponse]

@api_router.get("/public/users/{user_id}/profile", response_model=PublicUserProfileResponse)
async def get_public_user_profile(user_id: str):
    """Get a user's public profile with their public projects"""
    user = await db.users.find_one({"id": user_id}, {"_id": 0, "password": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's public projects
    projects = await db.projects.find(
        {"user_id": user_id, "is_public": True},
        {"_id": 0}
    ).sort("created_at", -1).to_list(1000)
    
    return PublicUserProfileResponse(
        id=user["id"],
        name=user["name"],
        projects=[ProjectResponse(**p) for p in projects]
    )

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

# ============ DIARY ROUTES ============

async def verify_project_access(project_id: str, user_id: str):
    project = await db.projects.find_one({"id": project_id, "user_id": user_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@api_router.post("/projects/{project_id}/diary", response_model=DiaryEntryResponse)
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
    return DiaryEntryResponse(**{k: v for k, v in entry_doc.items() if k != "_id"})

@api_router.get("/projects/{project_id}/diary", response_model=DiaryListResponse)
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
    
    return DiaryListResponse(entries=[DiaryEntryResponse(**e) for e in entries], total=total)

@api_router.get("/projects/{project_id}/diary/{entry_id}", response_model=DiaryEntryResponse)
async def get_diary_entry(
    project_id: str,
    entry_id: str,
    current_user: dict = Depends(get_current_user)
):
    await verify_project_access(project_id, current_user["id"])
    
    entry = await db.diary_entries.find_one({"id": entry_id, "project_id": project_id}, {"_id": 0})
    if not entry:
        raise HTTPException(status_code=404, detail="Diary entry not found")
    
    return DiaryEntryResponse(**entry)

@api_router.put("/projects/{project_id}/diary/{entry_id}", response_model=DiaryEntryResponse)
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
    return DiaryEntryResponse(**updated)

@api_router.delete("/projects/{project_id}/diary/{entry_id}", response_model=MessageResponse)
async def delete_diary_entry(
    project_id: str,
    entry_id: str,
    current_user: dict = Depends(get_current_user)
):
    await verify_project_access(project_id, current_user["id"])
    
    result = await db.diary_entries.delete_one({"id": entry_id, "project_id": project_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Diary entry not found")
    
    return MessageResponse(message="Diary entry deleted")

# ============ GALLERY ROUTES ============

@api_router.post("/projects/{project_id}/gallery/folders", response_model=GalleryFolderResponse)
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

@api_router.get("/projects/{project_id}/gallery", response_model=GalleryListResponse)
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

@api_router.put("/projects/{project_id}/gallery/folders/{folder_id}", response_model=GalleryFolderResponse)
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

@api_router.delete("/projects/{project_id}/gallery/folders/{folder_id}", response_model=MessageResponse)
async def delete_gallery_folder(
    project_id: str,
    folder_id: str,
    current_user: dict = Depends(get_current_user)
):
    await verify_project_access(project_id, current_user["id"])
    
    # Delete folder and all contents recursively
    async def delete_folder_recursive(fid: str):
        subfolders = await db.gallery_folders.find({"parent_id": fid}).to_list(1000)
        for subfolder in subfolders:
            await delete_folder_recursive(subfolder["id"])
        
        # Delete images in this folder
        images = await db.gallery_images.find({"folder_id": fid}).to_list(1000)
        for img in images:
            img_path = UPLOADS_DIR / img["url"].split("/uploads/")[-1]
            if img_path.exists():
                img_path.unlink()
        await db.gallery_images.delete_many({"folder_id": fid})
        await db.gallery_folders.delete_one({"id": fid})
    
    await delete_folder_recursive(folder_id)
    return MessageResponse(message="Folder and contents deleted")

@api_router.post("/projects/{project_id}/gallery/images", response_model=GalleryImageResponse)
async def upload_gallery_image(
    project_id: str,
    folder_id: Optional[str] = None,
    file: UploadFile = File(...),
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
    
    image_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    gallery_dir = UPLOADS_DIR / "gallery" / project_id
    gallery_dir.mkdir(parents=True, exist_ok=True)
    
    file_ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{image_id}.{file_ext}"
    file_path = gallery_dir / filename
    
    content = await file.read()
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

@api_router.delete("/projects/{project_id}/gallery/images/{image_id}", response_model=MessageResponse)
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

# ============ BLOG ROUTES ============

@api_router.post("/projects/{project_id}/blog", response_model=BlogEntryResponse)
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
    return BlogEntryResponse(**{k: v for k, v in entry_doc.items() if k != "_id"})

@api_router.get("/projects/{project_id}/blog", response_model=BlogListResponse)
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
    
    return BlogListResponse(entries=[BlogEntryResponse(**e) for e in entries], total=total)

@api_router.get("/projects/{project_id}/blog/{entry_id}", response_model=BlogEntryResponse)
async def get_blog_entry(
    project_id: str,
    entry_id: str,
    current_user: dict = Depends(get_current_user)
):
    await verify_project_access(project_id, current_user["id"])
    
    entry = await db.blog_entries.find_one({"id": entry_id, "project_id": project_id}, {"_id": 0})
    if not entry:
        raise HTTPException(status_code=404, detail="Blog entry not found")
    
    return BlogEntryResponse(**entry)

@api_router.put("/projects/{project_id}/blog/{entry_id}", response_model=BlogEntryResponse)
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
    return BlogEntryResponse(**updated)

@api_router.delete("/projects/{project_id}/blog/{entry_id}", response_model=MessageResponse)
async def delete_blog_entry(
    project_id: str,
    entry_id: str,
    current_user: dict = Depends(get_current_user)
):
    await verify_project_access(project_id, current_user["id"])
    
    result = await db.blog_entries.delete_one({"id": entry_id, "project_id": project_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Blog entry not found")
    
    return MessageResponse(message="Blog entry deleted")

# ============ LIBRARY ROUTES ============

@api_router.post("/projects/{project_id}/library/folders", response_model=LibraryFolderResponse)
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

@api_router.get("/projects/{project_id}/library", response_model=LibraryListResponse)
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
    
    return LibraryListResponse(
        folders=[LibraryFolderResponse(**f) for f in folders],
        entries=[LibraryEntryResponse(**e) for e in entries]
    )

@api_router.put("/projects/{project_id}/library/folders/{folder_id}", response_model=LibraryFolderResponse)
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

@api_router.delete("/projects/{project_id}/library/folders/{folder_id}", response_model=MessageResponse)
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

@api_router.post("/projects/{project_id}/library/entries", response_model=LibraryEntryResponse)
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
    return LibraryEntryResponse(**{k: v for k, v in entry_doc.items() if k != "_id"})

@api_router.get("/projects/{project_id}/library/entries/{entry_id}", response_model=LibraryEntryResponse)
async def get_library_entry(
    project_id: str,
    entry_id: str,
    current_user: dict = Depends(get_current_user)
):
    await verify_project_access(project_id, current_user["id"])
    
    entry = await db.library_entries.find_one({"id": entry_id, "project_id": project_id}, {"_id": 0})
    if not entry:
        raise HTTPException(status_code=404, detail="Library entry not found")
    
    return LibraryEntryResponse(**entry)

@api_router.put("/projects/{project_id}/library/entries/{entry_id}", response_model=LibraryEntryResponse)
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
    return LibraryEntryResponse(**updated)

@api_router.delete("/projects/{project_id}/library/entries/{entry_id}", response_model=MessageResponse)
async def delete_library_entry(
    project_id: str,
    entry_id: str,
    current_user: dict = Depends(get_current_user)
):
    await verify_project_access(project_id, current_user["id"])
    
    result = await db.library_entries.delete_one({"id": entry_id, "project_id": project_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Library entry not found")
    
    return MessageResponse(message="Library entry deleted")

# ============ PUBLIC BLOG/LIBRARY ROUTES ============

@api_router.get("/public/projects/{project_id}/blog", response_model=BlogListResponse)
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
    
    return BlogListResponse(entries=[BlogEntryResponse(**e) for e in entries], total=total)

@api_router.get("/public/projects/{project_id}/blog/{entry_id}", response_model=BlogEntryResponse)
async def get_public_blog_entry(project_id: str, entry_id: str):
    project = await db.projects.find_one({"id": project_id, "is_public": True})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    entry = await db.blog_entries.find_one({"id": entry_id, "project_id": project_id, "is_public": True}, {"_id": 0})
    if not entry:
        raise HTTPException(status_code=404, detail="Blog entry not found")
    
    await db.blog_entries.update_one({"id": entry_id}, {"$inc": {"views": 1}})
    entry["views"] = entry.get("views", 0) + 1
    
    return BlogEntryResponse(**entry)

@api_router.get("/public/projects/{project_id}/library", response_model=LibraryListResponse)
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

@api_router.get("/public/projects/{project_id}/library/entries/{entry_id}", response_model=LibraryEntryResponse)
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

# ============ PUBLIC GALLERY ROUTES ============

class PublicGalleryResponse(BaseModel):
    folders: List[GalleryFolderResponse]
    images: List[GalleryImageResponse]

@api_router.get("/public/projects/{project_id}/gallery", response_model=PublicGalleryResponse)
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
    
    # Query for public folders only
    folder_query = {"project_id": project_id, "is_public": True}
    if folder_id:
        folder_query["parent_id"] = folder_id
    else:
        folder_query["parent_id"] = None
    
    if search:
        folder_query["name"] = {"$regex": search, "$options": "i"}
    
    folders = await db.gallery_folders.find(folder_query, {"_id": 0}).sort(sort_by, sort_direction).to_list(1000)
    
    # Get images from public folders only
    public_folder_ids = [f["id"] for f in await db.gallery_folders.find({"project_id": project_id, "is_public": True}, {"_id": 0, "id": 1}).to_list(1000)]
    
    image_query = {"project_id": project_id}
    if folder_id:
        # If viewing a specific folder, only show images if that folder is public
        if folder_id not in public_folder_ids:
            return PublicGalleryResponse(folders=[], images=[])
        image_query["folder_id"] = folder_id
    else:
        # At root, show images from any public folder or root images of public folders
        image_query["$or"] = [
            {"folder_id": {"$in": public_folder_ids}},
            {"folder_id": None}  # Root images (if project has any public folders)
        ]
    
    if search:
        image_query["filename"] = {"$regex": search, "$options": "i"}
    
    images = await db.gallery_images.find(image_query, {"_id": 0}).sort(sort_by, sort_direction).to_list(1000)
    
    return PublicGalleryResponse(
        folders=[GalleryFolderResponse(**{**f, "is_public": f.get("is_public", False)}) for f in folders],
        images=[GalleryImageResponse(**i) for i in images]
    )

# ============ TASK ROUTES ============

@api_router.post("/projects/{project_id}/tasks", response_model=TaskResponse)
async def create_task(
    project_id: str,
    data: TaskCreate,
    current_user: dict = Depends(get_current_user)
):
    await verify_project_access(project_id, current_user["id"])
    
    task_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    task_doc = {
        "id": task_id,
        "project_id": project_id,
        "title": data.title,
        "description": data.description,
        "task_datetime": data.task_datetime,
        "is_all_day": data.is_all_day,
        "recurrence": data.recurrence,
        "created_at": now,
        "updated_at": now
    }
    
    await db.tasks.insert_one(task_doc)
    return TaskResponse(**{k: v for k, v in task_doc.items() if k != "_id"})

@api_router.get("/projects/{project_id}/tasks", response_model=TaskListResponse)
async def list_tasks(
    project_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    await verify_project_access(project_id, current_user["id"])
    
    query = {"project_id": project_id}
    
    if start_date and end_date:
        query["task_datetime"] = {"$gte": start_date, "$lte": end_date}
    
    total = await db.tasks.count_documents(query)
    tasks = await db.tasks.find(query, {"_id": 0}).sort("task_datetime", 1).to_list(1000)
    
    return TaskListResponse(tasks=[TaskResponse(**t) for t in tasks], total=total)

@api_router.get("/projects/{project_id}/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    project_id: str,
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    await verify_project_access(project_id, current_user["id"])
    
    task = await db.tasks.find_one({"id": task_id, "project_id": project_id}, {"_id": 0})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskResponse(**task)

@api_router.put("/projects/{project_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    project_id: str,
    task_id: str,
    data: TaskUpdate,
    current_user: dict = Depends(get_current_user)
):
    await verify_project_access(project_id, current_user["id"])
    
    task = await db.tasks.find_one({"id": task_id, "project_id": project_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.tasks.update_one({"id": task_id}, {"$set": update_data})
    updated = await db.tasks.find_one({"id": task_id}, {"_id": 0})
    return TaskResponse(**updated)

@api_router.delete("/projects/{project_id}/tasks/{task_id}", response_model=MessageResponse)
async def delete_task(
    project_id: str,
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    await verify_project_access(project_id, current_user["id"])
    
    result = await db.tasks.delete_one({"id": task_id, "project_id": project_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return MessageResponse(message="Task deleted")

# ============ ROUTINE ROUTES ============

@api_router.post("/projects/{project_id}/routines/{routine_type}", response_model=RoutineTaskResponse)
async def create_routine_task(
    project_id: str,
    routine_type: str,
    data: RoutineTaskCreate,
    current_user: dict = Depends(get_current_user)
):
    if routine_type not in ["startup", "shutdown"]:
        raise HTTPException(status_code=400, detail="Invalid routine type")
    
    await verify_project_access(project_id, current_user["id"])
    
    task_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    # Get max order
    max_order_doc = await db.routine_tasks.find_one(
        {"project_id": project_id, "routine_type": routine_type},
        sort=[("order", -1)]
    )
    max_order = max_order_doc["order"] + 1 if max_order_doc else 0
    
    task_doc = {
        "id": task_id,
        "project_id": project_id,
        "routine_type": routine_type,
        "title": data.title,
        "description": data.description,
        "order": data.order if data.order > 0 else max_order,
        "created_at": now
    }
    
    await db.routine_tasks.insert_one(task_doc)
    return RoutineTaskResponse(**{k: v for k, v in task_doc.items() if k != "_id"})

@api_router.get("/projects/{project_id}/routines/{routine_type}", response_model=RoutineListResponse)
async def list_routine_tasks(
    project_id: str,
    routine_type: str,
    date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    if routine_type not in ["startup", "shutdown"]:
        raise HTTPException(status_code=400, detail="Invalid routine type")
    
    await verify_project_access(project_id, current_user["id"])
    
    tasks = await db.routine_tasks.find(
        {"project_id": project_id, "routine_type": routine_type},
        {"_id": 0}
    ).sort("order", 1).to_list(1000)
    
    # Get completions for today (or specified date)
    check_date = date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    completions = await db.routine_completions.find(
        {"project_id": project_id, "routine_type": routine_type, "completed_date": check_date},
        {"_id": 0}
    ).to_list(1000)
    
    completed_task_ids = [c["task_id"] for c in completions]
    
    return RoutineListResponse(
        tasks=[RoutineTaskResponse(**t) for t in tasks],
        completions_today=completed_task_ids
    )

@api_router.put("/projects/{project_id}/routines/{routine_type}/{task_id}", response_model=RoutineTaskResponse)
async def update_routine_task(
    project_id: str,
    routine_type: str,
    task_id: str,
    data: RoutineTaskUpdate,
    current_user: dict = Depends(get_current_user)
):
    if routine_type not in ["startup", "shutdown"]:
        raise HTTPException(status_code=400, detail="Invalid routine type")
    
    await verify_project_access(project_id, current_user["id"])
    
    task = await db.routine_tasks.find_one({"id": task_id, "project_id": project_id, "routine_type": routine_type})
    if not task:
        raise HTTPException(status_code=404, detail="Routine task not found")
    
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    
    await db.routine_tasks.update_one({"id": task_id}, {"$set": update_data})
    updated = await db.routine_tasks.find_one({"id": task_id}, {"_id": 0})
    return RoutineTaskResponse(**updated)

@api_router.delete("/projects/{project_id}/routines/{routine_type}/{task_id}", response_model=MessageResponse)
async def delete_routine_task(
    project_id: str,
    routine_type: str,
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    if routine_type not in ["startup", "shutdown"]:
        raise HTTPException(status_code=400, detail="Invalid routine type")
    
    await verify_project_access(project_id, current_user["id"])
    
    result = await db.routine_tasks.delete_one({"id": task_id, "project_id": project_id, "routine_type": routine_type})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Routine task not found")
    
    # Also delete completions for this task
    await db.routine_completions.delete_many({"task_id": task_id})
    
    return MessageResponse(message="Routine task deleted")

@api_router.post("/projects/{project_id}/routines/{routine_type}/{task_id}/complete", response_model=MessageResponse)
async def toggle_routine_completion(
    project_id: str,
    routine_type: str,
    task_id: str,
    date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    if routine_type not in ["startup", "shutdown"]:
        raise HTTPException(status_code=400, detail="Invalid routine type")
    
    await verify_project_access(project_id, current_user["id"])
    
    task = await db.routine_tasks.find_one({"id": task_id, "project_id": project_id, "routine_type": routine_type})
    if not task:
        raise HTTPException(status_code=404, detail="Routine task not found")
    
    check_date = date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    # Check if already completed
    existing = await db.routine_completions.find_one({
        "task_id": task_id,
        "project_id": project_id,
        "routine_type": routine_type,
        "completed_date": check_date
    })
    
    if existing:
        # Un-complete
        await db.routine_completions.delete_one({"id": existing["id"]})
        return MessageResponse(message="Task marked as incomplete")
    else:
        # Complete
        completion_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        completion_doc = {
            "id": completion_id,
            "task_id": task_id,
            "project_id": project_id,
            "routine_type": routine_type,
            "completed_date": check_date,
            "created_at": now
        }
        
        await db.routine_completions.insert_one(completion_doc)
        return MessageResponse(message="Task marked as complete")

@api_router.put("/projects/{project_id}/routines/{routine_type}/reorder", response_model=MessageResponse)
async def reorder_routine_tasks(
    project_id: str,
    routine_type: str,
    task_ids: List[str],
    current_user: dict = Depends(get_current_user)
):
    if routine_type not in ["startup", "shutdown"]:
        raise HTTPException(status_code=400, detail="Invalid routine type")
    
    await verify_project_access(project_id, current_user["id"])
    
    for index, task_id in enumerate(task_ids):
        await db.routine_tasks.update_one(
            {"id": task_id, "project_id": project_id, "routine_type": routine_type},
            {"$set": {"order": index}}
        )
    
    return MessageResponse(message="Tasks reordered")

# ============ DASHBOARD DATA ============

@api_router.get("/dashboard/today")
async def get_dashboard_today(current_user: dict = Depends(get_current_user)):
    """Get today's tasks, startup and shutdown routines for dashboard"""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    today_start = f"{today}T00:00:00"
    today_end = f"{today}T23:59:59"
    
    # Get all user's projects
    projects = await db.projects.find({"user_id": current_user["id"]}, {"_id": 0}).to_list(1000)
    project_ids = [p["id"] for p in projects]
    
    if not project_ids:
        return {
            "today_tasks": [],
            "startup_tasks": [],
            "shutdown_tasks": [],
            "startup_completions": [],
            "shutdown_completions": []
        }
    
    # Get today's tasks (including recurring)
    tasks_query = {
        "project_id": {"$in": project_ids},
        "$or": [
            {"task_datetime": {"$gte": today_start, "$lte": today_end}},
            {"recurrence": {"$ne": None}}
        ]
    }
    tasks = await db.tasks.find(tasks_query, {"_id": 0}).to_list(1000)
    
    # Filter recurring tasks that apply to today
    today_tasks = []
    today_date = datetime.now(timezone.utc)
    day_of_week = today_date.weekday()
    day_of_month = today_date.day
    day_of_year = today_date.timetuple().tm_yday
    
    for task in tasks:
        task_dt = datetime.fromisoformat(task["task_datetime"].replace("Z", "+00:00"))
        
        if task["recurrence"] == "daily":
            today_tasks.append(task)
        elif task["recurrence"] == "weekly" and task_dt.weekday() == day_of_week:
            today_tasks.append(task)
        elif task["recurrence"] == "monthly" and task_dt.day == day_of_month:
            today_tasks.append(task)
        elif task["recurrence"] == "yearly" and task_dt.timetuple().tm_yday == day_of_year:
            today_tasks.append(task)
        elif task["recurrence"] is None and today_start <= task["task_datetime"] <= today_end:
            today_tasks.append(task)
    
    # Get routine tasks
    startup_tasks = await db.routine_tasks.find(
        {"project_id": {"$in": project_ids}, "routine_type": "startup"},
        {"_id": 0}
    ).sort("order", 1).to_list(1000)
    
    shutdown_tasks = await db.routine_tasks.find(
        {"project_id": {"$in": project_ids}, "routine_type": "shutdown"},
        {"_id": 0}
    ).sort("order", 1).to_list(1000)
    
    # Get completions for today
    startup_completions = await db.routine_completions.find(
        {"project_id": {"$in": project_ids}, "routine_type": "startup", "completed_date": today},
        {"_id": 0}
    ).to_list(1000)
    
    shutdown_completions = await db.routine_completions.find(
        {"project_id": {"$in": project_ids}, "routine_type": "shutdown", "completed_date": today},
        {"_id": 0}
    ).to_list(1000)
    
    return {
        "today_tasks": today_tasks,
        "startup_tasks": startup_tasks,
        "shutdown_tasks": shutdown_tasks,
        "startup_completions": [c["task_id"] for c in startup_completions],
        "shutdown_completions": [c["task_id"] for c in shutdown_completions]
    }

# ============ HEALTH CHECK ============

@api_router.get("/")
async def root():
    return {"message": f"{APP_NAME} API", "status": "healthy", "app_name": APP_NAME}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat(), "app_name": APP_NAME}

@api_router.get("/config")
async def get_app_config():
    """Get public app configuration"""
    return {
        "app_name": APP_NAME,
        "app_url": APP_URL,
        "email_configured": bool(SMTP_HOST and SMTP_USER)
    }

# ============ FOLDER PATH ENDPOINTS ============

@api_router.get("/projects/{project_id}/gallery/folders/{folder_id}/path")
async def get_gallery_folder_path(
    project_id: str,
    folder_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get the full path of a gallery folder for breadcrumb navigation"""
    await verify_project_access(project_id, current_user["id"])
    
    path = []
    current_id = folder_id
    
    while current_id:
        folder = await db.gallery_folders.find_one(
            {"id": current_id, "project_id": project_id},
            {"_id": 0}
        )
        if not folder:
            break
        path.insert(0, {"id": folder["id"], "name": folder["name"]})
        current_id = folder.get("parent_id")
    
    return {"path": path}

@api_router.get("/projects/{project_id}/library/folders/{folder_id}/path")
async def get_library_folder_path(
    project_id: str,
    folder_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get the full path of a library folder for breadcrumb navigation"""
    await verify_project_access(project_id, current_user["id"])
    
    path = []
    current_id = folder_id
    
    while current_id:
        folder = await db.library_folders.find_one(
            {"id": current_id, "project_id": project_id},
            {"_id": 0}
        )
        if not folder:
            break
        path.insert(0, {"id": folder["id"], "name": folder["name"]})
        current_id = folder.get("parent_id")
    
    return {"path": path}

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
    logger.info("Starting application...")
    
    # Create indexes
    await db.users.create_index("email", unique=True)
    await db.users.create_index("id", unique=True)
    await db.password_resets.create_index("token")
    await db.password_resets.create_index("user_id")
    await db.projects.create_index("id", unique=True)
    await db.projects.create_index("user_id")
    await db.projects.create_index("is_public")
    logger.info("Database indexes created")
    
    # Auto-seed admin user if no users exist
    try:
        user_count = await db.users.count_documents({})
        logger.info(f"Current user count: {user_count}")
        
        if user_count == 0:
            admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
            admin_email = os.environ.get('ADMIN_EMAIL', 'admin@selfsufficient.app')
            admin_name = os.environ.get('ADMIN_NAME', 'Admin')
            
            hashed = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt())
            now = datetime.now(timezone.utc).isoformat()
            
            result = await db.users.insert_one({
                "id": str(uuid.uuid4()),
                "email": admin_email,
                "password": hashed.decode('utf-8'),
                "name": admin_name,
                "is_admin": True,
                "daily_reminders": False,
                "created_at": now,
                "updated_at": now
            })
            logger.info(f"Admin user created: {admin_email} (inserted_id: {result.inserted_id})")
        else:
            logger.info(f"Skipping admin seed - {user_count} user(s) already exist")
    except Exception as e:
        logger.error(f"Error during admin seeding: {e}")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
