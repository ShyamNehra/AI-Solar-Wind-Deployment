from datetime import datetime
from pydantic import BaseModel


class SiteCreate(BaseModel):
    project_id: str
    name: str
    latitude: float
    longitude: float
    region: str | None = None
    land_area_sqkm: float | None = None
    elevation_m: float | None = None
    land_ownership: str | None = None


class SiteResponse(BaseModel):
    id: str
    project_id: str
    name: str
    latitude: float
    longitude: float
    region: str | None = None
    land_area_sqkm: float | None = None
    elevation_m: float | None = None
    land_ownership: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True
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
