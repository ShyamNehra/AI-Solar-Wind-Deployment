from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
from pydantic import BaseModel, Field

class ProjectCreate(BaseModel):
    project_name: str = Field(..., min_length=1)
    description: str
    state: str

    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
from datetime import datetime
from typing import Optional, List


class ProjectBase(BaseModel):
    project_name: str = Field(..., min_length=1)
    region: str = Field(..., min_length=1)
    description: Optional[str] = None
    status: Optional[str] = "Draft"


class ProjectCreate(ProjectBase):
    pass

class ProjectOut(ProjectBase):
    id: int
    created_at: datetime
    owner_id: int

class ProjectUpdate(BaseModel):
    project_name: Optional[str] = None
    region: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class ProjectResponse(ProjectBase):
    id: int
    created_date: datetime
    user_id: int

    class Config:
        from_attributes = True
