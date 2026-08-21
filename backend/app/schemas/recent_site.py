from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RecentSiteCreate(BaseModel):
    organization_id: str
    name: str
    latitude: float
    longitude: float
    status: Optional[str] = "EVALUATED"
    region: Optional[str] = None
    elevation: Optional[str] = None
    existing_infra: Optional[str] = None
    score: Optional[float] = None
    project_id: Optional[str] = None
    evaluated_by: Optional[str] = None

class RecentSiteOut(BaseModel):
    id: int
    organization_id: str
    name: str
    latitude: float
    longitude: float
    status: Optional[str] = None
    region: Optional[str] = None
    elevation: Optional[str] = None
    existing_infra: Optional[str] = None
    score: Optional[float] = None
    project_id: Optional[str] = None
    evaluated_by: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
