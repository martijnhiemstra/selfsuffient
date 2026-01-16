"""Task routes."""
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from datetime import datetime, timezone
import uuid

from config import db
from models import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse, MessageResponse
from services import get_current_user, verify_project_access

router = APIRouter()


@router.post("/projects/{project_id}/tasks", response_model=TaskResponse)
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


@router.get("/projects/{project_id}/tasks", response_model=TaskListResponse)
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


@router.get("/projects/{project_id}/tasks/{task_id}", response_model=TaskResponse)
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


@router.put("/projects/{project_id}/tasks/{task_id}", response_model=TaskResponse)
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


@router.delete("/projects/{project_id}/tasks/{task_id}", response_model=MessageResponse)
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
