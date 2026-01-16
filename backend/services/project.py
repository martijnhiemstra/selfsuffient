"""Project services."""
from fastapi import HTTPException
from config import db


async def verify_project_access(project_id: str, user_id: str):
    """Verify user has access to a project."""
    project = await db.projects.find_one({"id": project_id, "user_id": user_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
