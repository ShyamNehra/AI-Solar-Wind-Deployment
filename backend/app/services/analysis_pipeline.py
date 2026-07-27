from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from app.evaluation.scorer import SiteScorer, SiteMetrics, SiteEvaluationResult
from app.services.energy_estimator import (
    EnergyEstimationService,
    EnergyEstimationRequest,
    EnergyEstimationResult,
    DeploymentType
)
# 1. Pipeline Input / Output Schemas
class SiteAnalysisRequest(BaseModel):
    site_id: str
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    available_land_area_sqm: float = Field(..., gt=0.0)
    slope: float = Field(..., ge=0.0, le=90.0)
    env_sensitivity: float = Field(..., ge=0.0, le=1.0)
    distance_to_grid: float = Field(..., ge=0.0)
    
    # Feature inputs
    solar_irradiance: float = Field(default=5.2, ge=0.0)  # kWh/m2/day
    wind_speed: float = Field(default=6.1, ge=0.0)        # m/s
    
    # Capacity configurations
    solar_capacity_mw: float = Field(default=10.0, ge=0.0)
    wind_capacity_mw: float = Field(default=5.0, ge=0.0)
    technology: DeploymentType = Field(default=DeploymentType.HYBRID)


class DeploymentRecommendation(BaseModel):
    recommended_technology: DeploymentType
    recommended_solar_mw: float
    recommended_wind_mw: float
    estimated_annual_mwh: float
    expansion_feasible: bool
    reasoning: str


class ConsolidatedAnalysisResponse(BaseModel):
    site_id: str
    coordinates: Dict[str, float]
    solar_assessment: Dict[str, Any]
    wind_assessment: Dict[str, Any]
    site_evaluation: SiteEvaluationResult
    energy_yield: EnergyEstimationResult
    deployment_recommendation: DeploymentRecommendation

# 2. Pipeline Orchestrator Service
class AnalysisPipeline:
    def __init__(self):
        self.scorer = SiteScorer()
        self.estimator = EnergyEstimationService()

    def run(self, request: SiteAnalysisRequest) -> ConsolidatedAnalysisResponse:
        # Step 1: Retrieve Solar Features
        solar_data = {
            "irradiance_kwh_m2": request.solar_irradiance,
            "suitability": "High" if request.solar_irradiance >= 4.5 else "Moderate"
        }

        # Step 2: Retrieve Wind Features
        wind_data = {
            "wind_speed_m_s": request.wind_speed,
            "suitability": "High" if request.wind_speed >= 5.5 else "Moderate"
        }

        # Step 3 & 4: Evaluate Site & Calculate Site Score
        site_metrics = SiteMetrics(
            site_id=request.site_id,
            solar_irradiance=request.solar_irradiance,
            wind_speed=request.wind_speed,
            slope=request.slope,
            distance_to_grid=request.distance_to_grid,
            env_sensitivity=request.env_sensitivity,
            elevation=getattr(request, "elevation", 300.0),
            distance_to_road=getattr(request, "distance_to_road", 5.0),
            land_cost_per_sqm=getattr(request, "land_cost_per_sqm", 25.0)
        )
        evaluation_result = self.scorer.evaluate_site(site_metrics)

        # Step 5: Estimate Energy Yield
        estimation_req = EnergyEstimationRequest(
            site_id=request.site_id,
            deployment_type=request.technology,
            solar_capacity_mw=request.solar_capacity_mw,
            wind_capacity_mw=request.wind_capacity_mw,
            solar_capacity_factor=0.20,
            wind_capacity_factor=0.35
        )
        energy_result = self.estimator.estimate_energy(estimation_req)

        # Step 6: Generate Deployment Recommendation
        recommendation = self._generate_recommendation(
            request=request, 
            score=evaluation_result.overall_score, 
            annual_mwh=energy_result.total_annual_mwh
        )

        # Step 7: Consolidated Output
        return ConsolidatedAnalysisResponse(
            site_id=request.site_id,
            coordinates={"latitude": request.latitude, "longitude": request.longitude},
            solar_assessment=solar_data,
            wind_assessment=wind_data,
            site_evaluation=evaluation_result,
            energy_yield=energy_result,
            deployment_recommendation=recommendation
        )

    def _generate_recommendation(
        self, request: SiteAnalysisRequest, score: float, annual_mwh: float
    ) -> DeploymentRecommendation:
        # Business logic for optimization
        expansion_feasible = request.available_land_area_sqm > 50_000 and request.slope < 10.0
        
        if score >= 75.0:
            tech = DeploymentType.HYBRID
            reason = "High site score supports hybrid deployment with full capacity expansion."
        elif request.solar_irradiance > 5.0:
            tech = DeploymentType.SOLAR
            reason = "Solar irradiance favors dedicated solar deployment."
        else:
            tech = DeploymentType.WIND
            reason = "Wind resources are primary energy driver."

        return DeploymentRecommendation(
            recommended_technology=tech,
            recommended_solar_mw=request.solar_capacity_mw,
            recommended_wind_mw=request.wind_capacity_mw if tech != DeploymentType.SOLAR else 0.0,
            estimated_annual_mwh=annual_mwh,
            expansion_feasible=expansion_feasible,
            reasoning=reason
        )