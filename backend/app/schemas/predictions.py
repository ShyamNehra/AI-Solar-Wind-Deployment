from pydantic import BaseModel
from datetime import datetime

class SolarPredictionOut(BaseModel):
    id: int
    site_id: int
    annual_irradiance: float
    peak_sun_hours: float
    expected_energy_output: float
    capacity_factor: float
    performance_ratio: float
    model_type: str
    data_source: str
    formula_used: str
    formula_source: str
    capacity_factor_note: str
    is_trained_ml_model: bool
    model_note: str
    created_at: datetime

    class Config:
        from_attributes = True

class WindPredictionOut(BaseModel):
    id: int
    site_id: int
    average_wind_speed: float
    wind_power_density: float
    turbulence_intensity: float
    capacity_factor: float
    expected_annual_energy_production: float
    model_type: str
    data_source: str
    formula_used: str
    formula_source: str
    capacity_factor_note: str
    turbulence_formula_used: str
    turbulence_formula_source: str
    is_trained_ml_model: bool
    model_note: str
    created_at: datetime

    class Config:
        from_attributes = True
