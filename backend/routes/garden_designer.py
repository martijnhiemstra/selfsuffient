"""Garden Designer routes - AI-powered garden layout generation."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid

from config import db
from services import get_current_user
from services.garden_ai import GardenDesignerAI, GardenDesignResult
from routes.openai_settings import decrypt_api_key

router = APIRouter()


class GardenBoundary(BaseModel):
    """Garden boundary definition"""
    points: List[Dict[str, float]]  # [{x: float, y: float}, ...]
    scale: float  # meters per grid unit


class GardenDetailsInput(BaseModel):
    """User inputs for garden design"""
    latitude: float
    longitude: float
    wind_direction: str
    garden_goal: str
    plant_preferences: List[str]
    custom_plants: Optional[str] = None
    existing_features: Optional[List[str]] = None
    custom_features: Optional[str] = None
    notes: Optional[str] = None


class GenerateGardenRequest(BaseModel):
    """Request to generate a garden design"""
    project_id: str
    boundary: GardenBoundary
    details: GardenDetailsInput


class GardenDesignResponse(BaseModel):
    """Response with generated garden design"""
    id: str
    project_id: str
    created_at: str
    boundary: GardenBoundary
    details: GardenDetailsInput
    design: Dict[str, Any]  # The AI-generated design


class GardenDesignListResponse(BaseModel):
    """List of saved garden designs"""
    designs: List[Dict[str, Any]]
    total: int


@router.post("/generate", response_model=GardenDesignResponse)
async def generate_garden_design(
    data: GenerateGardenRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate a garden design using AI.
    Requires user to have an OpenAI API key configured.
    """
    # Verify project belongs to user
    project = await db.projects.find_one({
        "id": data.project_id,
        "user_id": current_user["id"]
    })
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get user's OpenAI API key
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    if not user.get("openai_api_key"):
        raise HTTPException(
            status_code=400,
            detail="OpenAI API key not configured. Please add your API key in Settings."
        )
    
    try:
        api_key = decrypt_api_key(user["openai_api_key"])
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Failed to decrypt API key. Please re-enter it in Settings."
        )
    
    model = user.get("openai_model", "gpt-4o-mini")
    
    # Generate the design
    try:
        ai = GardenDesignerAI(api_key, model)
        result = await ai.generate_design(
            boundary_points=data.boundary.points,
            scale=data.boundary.scale,
            latitude=data.details.latitude,
            longitude=data.details.longitude,
            wind_direction=data.details.wind_direction,
            garden_goal=data.details.garden_goal,
            plant_preferences=data.details.plant_preferences,
            custom_plants=data.details.custom_plants,
            existing_features=data.details.existing_features,
            custom_features=data.details.custom_features,
            notes=data.details.notes
        )
        
        # Convert result to dict
        design_dict = {
            "plants": [p.model_dump() for p in result.plants],
            "zones": [z.model_dump() for z in result.zones],
            "sun_analysis": result.sun_analysis,
            "wind_analysis": result.wind_analysis,
            "climate_info": result.climate_info,
            "design_summary": result.design_summary,
            "planting_tips": result.planting_tips,
            "seasonal_tasks": result.seasonal_tasks
        }
        
        # Save to database
        design_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        design_doc = {
            "id": design_id,
            "project_id": data.project_id,
            "user_id": current_user["id"],
            "boundary": data.boundary.model_dump(),
            "details": data.details.model_dump(),
            "design": design_dict,
            "created_at": now,
            "updated_at": now
        }
        
        await db.garden_designs.insert_one(design_doc)
        
        return GardenDesignResponse(
            id=design_id,
            project_id=data.project_id,
            created_at=now,
            boundary=data.boundary,
            details=data.details,
            design=design_dict
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate design: {str(e)}")


@router.get("/designs/{project_id}", response_model=GardenDesignListResponse)
async def get_garden_designs(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all saved garden designs for a project"""
    designs = await db.garden_designs.find(
        {"project_id": project_id, "user_id": current_user["id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
    return GardenDesignListResponse(
        designs=designs,
        total=len(designs)
    )


@router.get("/design/{design_id}", response_model=GardenDesignResponse)
async def get_garden_design(
    design_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific garden design"""
    design = await db.garden_designs.find_one(
        {"id": design_id, "user_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not design:
        raise HTTPException(status_code=404, detail="Design not found")
    
    return GardenDesignResponse(
        id=design["id"],
        project_id=design["project_id"],
        created_at=design["created_at"],
        boundary=GardenBoundary(**design["boundary"]),
        details=GardenDetailsInput(**design["details"]),
        design=design["design"]
    )


@router.delete("/design/{design_id}")
async def delete_garden_design(
    design_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a garden design"""
    result = await db.garden_designs.delete_one({
        "id": design_id,
        "user_id": current_user["id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Design not found")
    
    return {"message": "Design deleted successfully"}
