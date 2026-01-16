"""Routine routes."""
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone
import uuid

from config import db
from models import (
    RoutineTaskCreate, RoutineTaskUpdate, RoutineTaskResponse,
    RoutineListResponse, MessageResponse
)
from services import get_current_user, verify_project_access

router = APIRouter()


@router.post("/projects/{project_id}/routines/{routine_type}", response_model=RoutineTaskResponse)
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
    
    max_order_doc = await db.routine_tasks.find_one(
        {"project_id": project_id, "routine_type": routine_type},
        sort=[("order", -1)]
    )
    next_order = (max_order_doc["order"] + 1) if max_order_doc else 0
    
    task_doc = {
        "id": task_id,
        "project_id": project_id,
        "routine_type": routine_type,
        "title": data.title,
        "description": data.description,
        "order": data.order if data.order != 0 else next_order,
        "created_at": now
    }
    
    await db.routine_tasks.insert_one(task_doc)
    return RoutineTaskResponse(**{k: v for k, v in task_doc.items() if k != "_id"})


@router.get("/projects/{project_id}/routines/{routine_type}", response_model=RoutineListResponse)
async def list_routine_tasks(
    project_id: str,
    routine_type: str,
    current_user: dict = Depends(get_current_user)
):
    if routine_type not in ["startup", "shutdown"]:
        raise HTTPException(status_code=400, detail="Invalid routine type")
    
    await verify_project_access(project_id, current_user["id"])
    
    tasks = await db.routine_tasks.find(
        {"project_id": project_id, "routine_type": routine_type},
        {"_id": 0}
    ).sort("order", 1).to_list(1000)
    
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    completions = await db.routine_completions.find(
        {"completed_date": today},
        {"_id": 0}
    ).to_list(1000)
    
    task_ids = [t["id"] for t in tasks]
    completions_today = [c["task_id"] for c in completions if c["task_id"] in task_ids]
    
    return RoutineListResponse(
        tasks=[RoutineTaskResponse(**t) for t in tasks],
        completions_today=completions_today
    )


@router.put("/projects/{project_id}/routines/{routine_type}/{task_id}", response_model=RoutineTaskResponse)
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
    
    task = await db.routine_tasks.find_one({
        "id": task_id,
        "project_id": project_id,
        "routine_type": routine_type
    })
    
    if not task:
        raise HTTPException(status_code=404, detail="Routine task not found")
    
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    
    if update_data:
        await db.routine_tasks.update_one({"id": task_id}, {"$set": update_data})
    
    updated = await db.routine_tasks.find_one({"id": task_id}, {"_id": 0})
    return RoutineTaskResponse(**updated)


@router.delete("/projects/{project_id}/routines/{routine_type}/{task_id}", response_model=MessageResponse)
async def delete_routine_task(
    project_id: str,
    routine_type: str,
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    if routine_type not in ["startup", "shutdown"]:
        raise HTTPException(status_code=400, detail="Invalid routine type")
    
    await verify_project_access(project_id, current_user["id"])
    
    result = await db.routine_tasks.delete_one({
        "id": task_id,
        "project_id": project_id,
        "routine_type": routine_type
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Routine task not found")
    
    await db.routine_completions.delete_many({"task_id": task_id})
    
    return MessageResponse(message="Routine task deleted")


@router.post("/projects/{project_id}/routines/{routine_type}/{task_id}/complete", response_model=MessageResponse)
async def complete_routine_task(
    project_id: str,
    routine_type: str,
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    if routine_type not in ["startup", "shutdown"]:
        raise HTTPException(status_code=400, detail="Invalid routine type")
    
    await verify_project_access(project_id, current_user["id"])
    
    task = await db.routine_tasks.find_one({
        "id": task_id,
        "project_id": project_id,
        "routine_type": routine_type
    })
    
    if not task:
        raise HTTPException(status_code=404, detail="Routine task not found")
    
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    existing = await db.routine_completions.find_one({
        "task_id": task_id,
        "completed_date": today
    })
    
    if existing:
        return MessageResponse(message="Task already completed today")
    
    completion_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    await db.routine_completions.insert_one({
        "id": completion_id,
        "task_id": task_id,
        "completed_date": today,
        "created_at": now
    })
    
    return MessageResponse(message="Task marked as complete")


@router.delete("/projects/{project_id}/routines/{routine_type}/{task_id}/complete", response_model=MessageResponse)
async def uncomplete_routine_task(
    project_id: str,
    routine_type: str,
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    if routine_type not in ["startup", "shutdown"]:
        raise HTTPException(status_code=400, detail="Invalid routine type")
    
    await verify_project_access(project_id, current_user["id"])
    
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    result = await db.routine_completions.delete_one({
        "task_id": task_id,
        "completed_date": today
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Completion not found")
    
    return MessageResponse(message="Task marked as incomplete")
