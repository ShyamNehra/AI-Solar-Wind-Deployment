from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class SiteBase(BaseModel):
    name: str
    latitude: float
    longitude: float
    land_area: Optional[float] = None
    elevation: Optional[float] = None
    existing_infrastructure: Optional[str] = None
    land_ownership: Optional[str] = None

class SiteCreate(SiteBase):
    pass

class SiteOut(BaseModel):
    id: int
    project_id: int
    name: str
    latitude: float
    longitude: float
    land_area: Optional[float] = None
    elevation: Optional[float] = None
    existing_infrastructure: Optional[str] = None
    land_ownership: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class SiteCompareOut(BaseModel):
    site1: SiteOut
    site2: SiteOut
    elevation_difference: float
    distance_km: float
