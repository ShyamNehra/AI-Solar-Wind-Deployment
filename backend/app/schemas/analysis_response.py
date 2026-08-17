from typing import Any, Dict, List

from pydantic import BaseModel


class AnalysisResponse(BaseModel):

    location: Dict[str, Any]

    location_validation: Dict[str, Any]

    environmental_data: Dict[str, Any]

    site_suitability: Dict[str, Any]

    recommended_deployment: Dict[str, Any]

    technical_feasibility: Dict[str, Any]

    energy_yield: Dict[str, Any]

    financial_metrics: Dict[str, Any]

    recommendation_reason: List[str]

    final_recommendation: str