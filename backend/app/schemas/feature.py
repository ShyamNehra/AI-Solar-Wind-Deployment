from datetime import datetime
from pydantic import BaseModel


class FeatureCreate(BaseModel):
    latitude: float
    longitude: float
    solar_irradiance: float
    wind_speed: float
    temperature: float
    humidity: float
    elevation: float
    slope: float


class FeatureResponse(FeatureCreate):
    id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }