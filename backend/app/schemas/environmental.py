from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict

class EnvironmentalDataOut(BaseModel):
    id: int
    site_id: int
    average_solar_irradiance: Optional[float] = None
    average_wind_speed: Optional[float] = None
    average_wind_direction: Optional[float] = None
    average_temperature: Optional[float] = None
    average_elevation: Optional[float] = None
    average_slope: Optional[float] = None
    land_cover_type: Optional[str] = None
    nearest_road_km: Optional[float] = None
    nearest_substation_km: Optional[float] = None
    nearest_urban_area_km: Optional[float] = None
    nearest_protected_zone_km: Optional[float] = None
    nearest_water_body_km: Optional[float] = None
    last_fetched_at: datetime
    data_sources: Dict[str, str]
    warnings: Optional[str] = None
