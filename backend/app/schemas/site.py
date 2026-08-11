from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


# ------------------------------------------------------------------------------
# EXISTING SCHEMAS (Preserved)
# ------------------------------------------------------------------------------

class SiteCreateSchema(BaseModel):
    project_id: int
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude must be between -90 and 90")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude must be between -180 and 180")
    area_sq_meters: float = Field(..., gt=0.0, description="Area must be a positive number greater than 0")

    class Config:
        from_attributes = True


# ------------------------------------------------------------------------------
# NEW STANDARDIZED API SCHEMAS
# ------------------------------------------------------------------------------

class SiteCoordinates(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)


class StandardizedSiteAssessmentRequest(BaseModel):
    site_id: str = Field(default="SITE_DEFAULT")
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    available_land_area_sqm: float = Field(default=100000.0, gt=0.0)
    slope: float = Field(default=3.0, ge=0.0, le=90.0)
    env_sensitivity: float = Field(default=0.1, ge=0.0, le=1.0)
    distance_to_grid: float = Field(default=2.5, ge=0.0)
    solar_irradiance: float = Field(default=5.2, ge=0.0)
    wind_speed: float = Field(default=6.1, ge=0.0)
    solar_capacity_mw: float = Field(default=10.0, ge=0.0)
    wind_capacity_mw: float = Field(default=5.0, ge=0.0)
    electricity_tariff: float = Field(default=4.50, gt=0.0, description="Electricity Tariff in INR/kWh")


class StandardizedFinalResponse(BaseModel):
    site_id: str
    coordinates: SiteCoordinates
    site_suitability: Dict[str, Any]
    recommended_deployment: str
    technical_feasibility: Dict[str, Any]
    ml_prediction: Dict[str, Any]
    energy_yield: Dict[str, Any]
    financial_metrics: Dict[str, Any]
    recommendation_reasoning: str
    status: str = Field(default="SUCCESS")