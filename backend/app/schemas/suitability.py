from datetime import datetime
from pydantic import BaseModel


class SuitabilityScoreResponse(BaseModel):
    id: str
    site_id: str
    overall_score: float
    solar_score: float
    wind_score: float
    infrastructure_score: float
    recommendation: str
    risks: list[str]
    created_at: datetime

    class Config:
        from_attributes = True