from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.pipeline import run_site_analysis_pipeline

router = APIRouter(prefix="/api/analysis", tags=["Analysis"])

class AnalysisRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, description="Latitude of candidate site")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude of candidate site")
    area_sq_m: float = Field(..., gt=0, description="Total land area available in square meters")
    electricity_tariff_inr_kwh: float = Field(5.5, gt=0, description="Target price per kWh in INR")
    
    # Optional overrides for advanced assessment
    month: int = Field(6, ge=1, le=12)
    day: int = Field(15, ge=1, le=31)
    temp_c: float = Field(28.0, ge=-20, le=60)
    wind_speed_ms: float = Field(6.5, ge=0, le=50)
    slope_deg: float = Field(2.5, ge=0, le=90)
    elevation_m: float = Field(920.0, ge=-100, le=9000)
    dist_grid_m: float = Field(1200.0, ge=0)
    dist_road_m: float = Field(400.0, ge=0)

@router.post("")
def run_analysis(payload: AnalysisRequest):
    try:
        result = run_site_analysis_pipeline(
            latitude=payload.latitude,
            longitude=payload.longitude,
            area_sq_m=payload.area_sq_m,
            electricity_tariff_inr_kwh=payload.electricity_tariff_inr_kwh,
            month=payload.month,
            day=payload.day,
            temp_c=payload.temp_c,
            wind_speed_ms=payload.wind_speed_ms,
            slope_deg=payload.slope_deg,
            elevation_m=payload.elevation_m,
            dist_grid_m=payload.dist_grid_m,
            dist_road_m=payload.dist_road_m
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")
