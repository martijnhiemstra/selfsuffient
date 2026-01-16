"""
Self-Sufficient Life - Main Application Entry Point

A full-stack application for managing self-sufficient lifestyle projects,
including diary entries, galleries, blogs, libraries, tasks, and daily routines.
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
import os

from config import APP_NAME, UPLOADS_DIR, db, logger
from routes import api_router
from services import hash_password


# Create the main app
app = FastAPI(title=APP_NAME)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploads
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

# Include all API routes
app.include_router(api_router)


@app.on_event("startup")
async def startup_event():
    """Seed admin user on startup if configured"""
    admin_email = os.environ.get('ADMIN_EMAIL', '')
    admin_password = os.environ.get('ADMIN_PASSWORD', '')
    
    if admin_email and admin_password:
        admin_exists = await db.users.find_one({"email": admin_email})
        if not admin_exists:
            from datetime import datetime, timezone
            import uuid
            
            admin_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc).isoformat()
            
            admin_doc = {
                "id": admin_id,
                "email": admin_email,
                "password": hash_password(admin_password),
                "name": "Admin",
                "is_admin": True,
                "daily_reminders": False,
                "created_at": now,
                "updated_at": now
            }
            
            await db.users.insert_one(admin_doc)
            logger.info(f"Admin user created: {admin_email}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
