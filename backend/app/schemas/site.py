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