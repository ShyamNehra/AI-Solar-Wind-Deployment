from datetime import datetime
from pydantic import BaseModel, ConfigDict


class FeatureBase(BaseModel):
    latitude: float
    longitude: float
    solar_irradiance: float
    wind_speed: float
    temperature: float
    humidity: float
    elevation: float
    slope: float


class FeatureCreate(FeatureBase):
    pass


class FeatureResponse(FeatureBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
