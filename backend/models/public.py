"""Public-facing Pydantic models."""
from pydantic import BaseModel
from typing import List
from .project import ProjectResponse


class PublicUserProfileResponse(BaseModel):
    id: str
    name: str
    projects: List[ProjectResponse]
