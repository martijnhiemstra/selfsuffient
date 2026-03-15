"""Checklist routes - Project checklists with reusable items."""
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List
from datetime import datetime, timezone
import uuid

from config import db
from models.checklist import (
    ChecklistCreate, ChecklistUpdate, ChecklistResponse, ChecklistListResponse,
    ChecklistItemCreate, ChecklistItemUpdate, ChecklistItemResponse
)
from models import MessageResponse
from services import get_current_user

router = APIRouter()


# ============ CHECKLISTS ============

@router.post("/checklists", response_model=ChecklistResponse)
async def create_checklist(data: ChecklistCreate, current_user: dict = Depends(get_current_user)):
    """Create a new checklist for a project."""
    # Verify project access
    project = await db.projects.find_one({"id": data.project_id, "user_id": current_user["id"]})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    checklist_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    checklist_doc = {
        "id": checklist_id,
        "user_id": current_user["id"],
        "project_id": data.project_id,
        "name": data.name,
        "description": data.description,
        "created_at": now,
        "updated_at": now
    }
    
    await db.checklists.insert_one(checklist_doc)
    
    return ChecklistResponse(
        id=checklist_id,
        project_id=data.project_id,
        project_name=project["name"],
        name=data.name,
        description=data.description,
        items=[],
        total_items=0,
        completed_items=0,
        created_at=now,
        updated_at=now
    )


@router.get("/checklists", response_model=ChecklistListResponse)
async def list_checklists(
    project_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """List all checklists, optionally filtered by project."""
    query = {"user_id": current_user["id"]}
    if project_id:
        query["project_id"] = project_id
    
    checklists = await db.checklists.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
    
    result = []
    for checklist in checklists:
        # Get project name
        project = await db.projects.find_one({"id": checklist["project_id"]}, {"_id": 0, "name": 1})
        
        # Get items for this checklist
        items = await db.checklist_items.find(
            {"checklist_id": checklist["id"]}, 
            {"_id": 0}
        ).sort("order", 1).to_list(1000)
        
        item_responses = [ChecklistItemResponse(**item) for item in items]
        total_items = len(items)
        completed_items = sum(1 for item in items if item.get("is_done", False))
        
        result.append(ChecklistResponse(
            **checklist,
            project_name=project["name"] if project else None,
            items=item_responses,
            total_items=total_items,
            completed_items=completed_items
        ))
    
    return ChecklistListResponse(checklists=result, total=len(result))


@router.get("/checklists/{checklist_id}", response_model=ChecklistResponse)
async def get_checklist(checklist_id: str, current_user: dict = Depends(get_current_user)):
    """Get a single checklist with all its items."""
    checklist = await db.checklists.find_one(
        {"id": checklist_id, "user_id": current_user["id"]},
        {"_id": 0}
    )
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist not found")
    
    # Get project name
    project = await db.projects.find_one({"id": checklist["project_id"]}, {"_id": 0, "name": 1})
    
    # Get items
    items = await db.checklist_items.find(
        {"checklist_id": checklist_id},
        {"_id": 0}
    ).sort("order", 1).to_list(1000)
    
    item_responses = [ChecklistItemResponse(**item) for item in items]
    total_items = len(items)
    completed_items = sum(1 for item in items if item.get("is_done", False))
    
    return ChecklistResponse(
        **checklist,
        project_name=project["name"] if project else None,
        items=item_responses,
        total_items=total_items,
        completed_items=completed_items
    )


@router.put("/checklists/{checklist_id}", response_model=ChecklistResponse)
async def update_checklist(
    checklist_id: str,
    data: ChecklistUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a checklist."""
    checklist = await db.checklists.find_one({"id": checklist_id, "user_id": current_user["id"]})
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist not found")
    
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.checklists.update_one({"id": checklist_id}, {"$set": update_data})
    
    return await get_checklist(checklist_id, current_user)


@router.delete("/checklists/{checklist_id}", response_model=MessageResponse)
async def delete_checklist(checklist_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a checklist and all its items."""
    checklist = await db.checklists.find_one({"id": checklist_id, "user_id": current_user["id"]})
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist not found")
    
    # Delete all items first
    await db.checklist_items.delete_many({"checklist_id": checklist_id})
    
    # Delete checklist
    await db.checklists.delete_one({"id": checklist_id})
    
    return MessageResponse(message="Checklist deleted")


@router.post("/checklists/{checklist_id}/reset", response_model=ChecklistResponse)
async def reset_checklist(checklist_id: str, current_user: dict = Depends(get_current_user)):
    """Reset all items in a checklist to not done."""
    checklist = await db.checklists.find_one({"id": checklist_id, "user_id": current_user["id"]})
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist not found")
    
    now = datetime.now(timezone.utc).isoformat()
    
    # Reset all items
    await db.checklist_items.update_many(
        {"checklist_id": checklist_id},
        {"$set": {"is_done": False, "updated_at": now}}
    )
    
    # Update checklist timestamp
    await db.checklists.update_one(
        {"id": checklist_id},
        {"$set": {"updated_at": now}}
    )
    
    return await get_checklist(checklist_id, current_user)


# ============ CHECKLIST ITEMS ============

@router.post("/checklists/{checklist_id}/items", response_model=ChecklistItemResponse)
async def create_checklist_item(
    checklist_id: str,
    data: ChecklistItemCreate,
    current_user: dict = Depends(get_current_user)
):
    """Add an item to a checklist."""
    checklist = await db.checklists.find_one({"id": checklist_id, "user_id": current_user["id"]})
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist not found")
    
    # Get max order if not specified
    if data.order == 0:
        max_order_item = await db.checklist_items.find_one(
            {"checklist_id": checklist_id},
            sort=[("order", -1)]
        )
        data.order = (max_order_item["order"] + 1) if max_order_item else 1
    
    item_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    item_doc = {
        "id": item_id,
        "checklist_id": checklist_id,
        "text": data.text,
        "is_done": False,
        "order": data.order,
        "created_at": now,
        "updated_at": now
    }
    
    await db.checklist_items.insert_one(item_doc)
    
    # Update checklist timestamp
    await db.checklists.update_one(
        {"id": checklist_id},
        {"$set": {"updated_at": now}}
    )
    
    return ChecklistItemResponse(**item_doc)


@router.put("/checklist-items/{item_id}", response_model=ChecklistItemResponse)
async def update_checklist_item(
    item_id: str,
    data: ChecklistItemUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a checklist item (text, done status, order)."""
    item = await db.checklist_items.find_one({"id": item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Verify ownership through checklist
    checklist = await db.checklists.find_one({"id": item["checklist_id"], "user_id": current_user["id"]})
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist not found")
    
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.checklist_items.update_one({"id": item_id}, {"$set": update_data})
    
    updated = await db.checklist_items.find_one({"id": item_id}, {"_id": 0})
    return ChecklistItemResponse(**updated)


@router.delete("/checklist-items/{item_id}", response_model=MessageResponse)
async def delete_checklist_item(item_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a checklist item."""
    item = await db.checklist_items.find_one({"id": item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Verify ownership through checklist
    checklist = await db.checklists.find_one({"id": item["checklist_id"], "user_id": current_user["id"]})
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist not found")
    
    await db.checklist_items.delete_one({"id": item_id})
    
    # Update checklist timestamp
    await db.checklists.update_one(
        {"id": item["checklist_id"]},
        {"$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return MessageResponse(message="Item deleted")


@router.post("/checklist-items/{item_id}/toggle", response_model=ChecklistItemResponse)
async def toggle_checklist_item(item_id: str, current_user: dict = Depends(get_current_user)):
    """Toggle the done status of a checklist item."""
    item = await db.checklist_items.find_one({"id": item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Verify ownership through checklist
    checklist = await db.checklists.find_one({"id": item["checklist_id"], "user_id": current_user["id"]})
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist not found")
    
    now = datetime.now(timezone.utc).isoformat()
    new_status = not item.get("is_done", False)
    
    await db.checklist_items.update_one(
        {"id": item_id},
        {"$set": {"is_done": new_status, "updated_at": now}}
    )
    
    updated = await db.checklist_items.find_one({"id": item_id}, {"_id": 0})
    return ChecklistItemResponse(**updated)
