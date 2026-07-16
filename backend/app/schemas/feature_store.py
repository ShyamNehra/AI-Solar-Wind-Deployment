from pydantic import BaseModel, Field
from datetime import datetime

class FeatureBase(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Valid latitude parameter range")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Valid longitude parameter range")
    solar_irradiance: float = Field(..., ge=0.0)
    wind_speed: float = Field(..., ge=0.0)
    temperature: float
    humidity: float = Field(..., ge=0.0, le=100.0)
    elevation: float
    slope: float = Field(..., ge=0.0, le=90.0)

class FeatureCreate(FeatureBase):
    """Schema applied when writing new records to the database."""
    pass

class FeatureResponse(FeatureBase):
    """Schema applied when returning stored records back to the client UI."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True