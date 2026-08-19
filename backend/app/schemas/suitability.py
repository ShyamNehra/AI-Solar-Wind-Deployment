from pydantic import BaseModel
from typing import Dict, Any

class SuitabilityScoreBreakdown(BaseModel):
    resource_score: float
    geographic_score: float
    infrastructure_score: float
    environmental_score: float
    economic_score: float
    overall_deployment_score: float
    suitability_category: str
    capacity_factor: float

class SuitabilityDisclosures(BaseModel):
    formula_used: str
    formula_source: str
    economic_score_note: str
    environmental_score_note: str
    infrastructure_score_note: str

class SuitabilityOut(BaseModel):
    site_id: int
    solar: SuitabilityScoreBreakdown
    wind: SuitabilityScoreBreakdown
    disclosures: SuitabilityDisclosures
