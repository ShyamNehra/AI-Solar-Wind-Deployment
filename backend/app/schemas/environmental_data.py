from datetime import datetime
from pydantic import BaseModel


class EnvironmentalDataResponse(BaseModel):
    id: str
    site_id: str
    solar_irradiance_kwh_m2: float | None = None
    temperature_c: float | None = None
    cloud_cover_pct: float | None = None
    rainfall_mm: float | None = None
    wind_speed_ms: float | None = None
    wind_direction_deg: float | None = None
    elevation_m: float | None = None
    land_slope_deg: float | None = None
    vegetation_index_ndvi: float | None = None
    distance_to_roads_km: float | None = None
    distance_to_grid_km: float | None = None
    distance_to_substation_km: float | None = None
    created_at: datetime

    class Config:
        from_attributes = True