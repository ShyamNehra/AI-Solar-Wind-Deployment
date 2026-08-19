from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime

class SeasonalForecastOut(BaseModel):
    site_id: int
    solar_seasonal_kwh: Dict[str, float]
    wind_seasonal_kwh: Dict[str, float]
    formula_used: str
    formula_source: str

    class Config:
        from_attributes = True

class LongTermForecastOut(BaseModel):
    site_id: int
    solar_longterm_kwh: List[float]
    wind_longterm_kwh: List[float]
    degradation_rate_solar: float
    degradation_rate_wind: float
    degradation_rate_source: str

    class Config:
        from_attributes = True

class RevenueForecastOut(BaseModel):
    site_id: int
    solar_annual_revenue: float
    wind_annual_revenue: float
    combined_annual_revenue: float
    electricity_rate_usd_kwh: float
    electricity_rate_source: str
    grid_contribution_ratio: float
    grid_contribution_note: str

    class Config:
        from_attributes = True
