from pydantic import BaseModel
from typing import List, Dict, Any

class SiteOptimizationDetail(BaseModel):
    site_id: int
    site_name: str
    overall_deployment_score: float
    solar_score: float
    wind_score: float
    technology_recommendation: str
    recommended_capacity_kw: float
    co_location_viability: bool
    expansion_priority: int

class OptimizationOut(BaseModel):
    project_id: int
    ranked_site_ids: List[int]
    recommendations: List[SiteOptimizationDetail]
    capacity_density_solar_source: str
    capacity_density_wind_source: str

    class Config:
        from_attributes = True
