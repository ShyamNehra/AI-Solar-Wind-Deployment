from pydantic import BaseModel
from typing import Optional

class SiteScoreOut(BaseModel):
    id: int
    site_id: int
    solar_score: float
    wind_score: float
    renewable_resource_score: float
    geographic_score: float
    infrastructure_score: float
    environmental_score: float
    economic_score: float
    overall_deployment_score: float
    suitability_category: str
    formula_used: str
    formula_source: str
    economic_score_note: str
    environmental_score_note: str
    infrastructure_score_note: str

    class Config:
        from_attributes = True
