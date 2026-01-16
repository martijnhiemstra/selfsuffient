"""Dashboard routes."""
from fastapi import APIRouter, Depends
from datetime import datetime, timezone
from typing import List

from config import db
from models import TaskResponse, RoutineTaskResponse
from services import get_current_user

router = APIRouter()


class DashboardData:
    pass


@router.get("/data")
async def get_dashboard_data(current_user: dict = Depends(get_current_user)):
    """Get dashboard data including today's tasks and incomplete routines"""
    user_id = current_user["id"]
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    today_start = f"{today}T00:00:00"
    today_end = f"{today}T23:59:59"
    
    # Get user's projects
    projects = await db.projects.find({"user_id": user_id}, {"_id": 0}).to_list(1000)
    project_ids = [p["id"] for p in projects]
    
    # Get today's tasks from all projects
    tasks = await db.tasks.find({
        "project_id": {"$in": project_ids},
        "task_datetime": {"$gte": today_start, "$lte": today_end}
    }, {"_id": 0}).sort("task_datetime", 1).to_list(1000)
    
    # Get all routine tasks
    startup_tasks = await db.routine_tasks.find({
        "project_id": {"$in": project_ids},
        "routine_type": "startup"
    }, {"_id": 0}).sort("order", 1).to_list(1000)
    
    shutdown_tasks = await db.routine_tasks.find({
        "project_id": {"$in": project_ids},
        "routine_type": "shutdown"
    }, {"_id": 0}).sort("order", 1).to_list(1000)
    
    # Get today's completions
    completions = await db.routine_completions.find({
        "completed_date": today
    }, {"_id": 0}).to_list(1000)
    completed_task_ids = [c["task_id"] for c in completions]
    
    # Filter to incomplete tasks
    incomplete_startup = [t for t in startup_tasks if t["id"] not in completed_task_ids]
    incomplete_shutdown = [t for t in shutdown_tasks if t["id"] not in completed_task_ids]
    
    # Map tasks to their projects
    project_map = {p["id"]: p["name"] for p in projects}
    
    for task in tasks:
        task["project_name"] = project_map.get(task["project_id"], "Unknown")
    
    for task in incomplete_startup:
        task["project_name"] = project_map.get(task["project_id"], "Unknown")
    
    for task in incomplete_shutdown:
        task["project_name"] = project_map.get(task["project_id"], "Unknown")
    
    return {
        "today_tasks": tasks,
        "incomplete_startup_tasks": incomplete_startup,
        "incomplete_shutdown_tasks": incomplete_shutdown,
        "projects_count": len(projects),
        "date": today
    }


@router.get("/all-tasks")
async def get_all_user_tasks(
    start_date: str = None,
    end_date: str = None,
    current_user: dict = Depends(get_current_user)
):
    """Get all tasks across all user's projects for calendar view"""
    user_id = current_user["id"]
    
    projects = await db.projects.find({"user_id": user_id}, {"_id": 0, "id": 1, "name": 1}).to_list(1000)
    project_ids = [p["id"] for p in projects]
    project_map = {p["id"]: p["name"] for p in projects}
    
    query = {"project_id": {"$in": project_ids}}
    
    if start_date and end_date:
        query["task_datetime"] = {"$gte": start_date, "$lte": end_date}
    
    tasks = await db.tasks.find(query, {"_id": 0}).sort("task_datetime", 1).to_list(1000)
    
    for task in tasks:
        task["project_name"] = project_map.get(task["project_id"], "Unknown")
    
    return {"tasks": tasks, "total": len(tasks)}
