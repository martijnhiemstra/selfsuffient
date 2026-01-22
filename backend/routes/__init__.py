"""API routes initialization."""
from fastapi import APIRouter

# Create the main API router
api_router = APIRouter(prefix="/api")

# Import and include all route modules
from .auth import router as auth_router
from .admin import router as admin_router
from .projects import router as projects_router
from .diary import router as diary_router
from .gallery import router as gallery_router
from .blog import router as blog_router
from .library import router as library_router
from .tasks import router as tasks_router
from .routines import router as routines_router
from .public import router as public_router
from .dashboard import router as dashboard_router
from .health import router as health_router
from .finance import router as finance_router

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(admin_router, prefix="/admin", tags=["Admin"])
api_router.include_router(projects_router, prefix="/projects", tags=["Projects"])
api_router.include_router(diary_router, tags=["Diary"])
api_router.include_router(gallery_router, tags=["Gallery"])
api_router.include_router(blog_router, tags=["Blog"])
api_router.include_router(library_router, tags=["Library"])
api_router.include_router(tasks_router, tags=["Tasks"])
api_router.include_router(routines_router, tags=["Routines"])
api_router.include_router(public_router, prefix="/public", tags=["Public"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(health_router, tags=["Health"])
api_router.include_router(finance_router, prefix="/finance", tags=["Finance"])
