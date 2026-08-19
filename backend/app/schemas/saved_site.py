from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SavedSiteCreate(BaseModel):
    organization_id: str
    name: str
    description: Optional[str] = None
    latitude: float
    longitude: float
    status: Optional[str] = "APPROVED"
    score: Optional[float] = 85.0

class SavedSiteOut(BaseModel):
    id: int
    organization_id: str
    name: str
    description: Optional[str] = None
    latitude: float
    longitude: float
    status: str
    score: float
    created_at: datetime

    class Config:
        from_attributes = True
