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
from pydantic import BaseModel, Field
from typing import Optional


class SiteBase(BaseModel):
    site_name: Optional[str] = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    elevation: Optional[float] = None
    land_area: Optional[float] = None
    region: Optional[str] = None
    infrastructure: Optional[str] = None
    ownership: Optional[str] = None


class SiteCreate(SiteBase):
    project_id: int


class SiteUpdate(BaseModel):
    site_name: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    elevation: Optional[float] = None
    land_area: Optional[float] = None
    region: Optional[str] = None
    infrastructure: Optional[str] = None
    ownership: Optional[str] = None
    project_id: Optional[int] = None


class SiteResponse(SiteBase):
    id: int
    project_id: int

    class Config:
        from_attributes = True
