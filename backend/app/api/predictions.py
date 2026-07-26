from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

# Imports from your evaluation & services modules
from app.evaluation.scorer import SiteScorer, SiteMetrics, SiteEvaluationResult
from app.services.energy_estimator import (
    EnergyEstimationService, 
    EnergyEstimationRequest, 
    EnergyEstimationResult, 
    DeploymentType
)

router = APIRouter(prefix="/predictions", tags=["Predictions & Evaluation"])

# Initialize Services
scorer = SiteScorer()
estimator = EnergyEstimationService()


class FullSiteAssessmentRequest(BaseModel):
    site_metrics: SiteMetrics
    technology: DeploymentType
    solar_capacity_mw: float = Field(default=0.0, ge=0.0)
    wind_capacity_mw: float = Field(default=0.0, ge=0.0)
    solar_capacity_factor: float = Field(default=0.20, ge=0.0, le=1.0)
    wind_capacity_factor: float = Field(default=0.35, ge=0.0, le=1.0)


class FullSiteAssessmentResponse(BaseModel):
    evaluation: SiteEvaluationResult
    energy_yield: EnergyEstimationResult


@router.post("/evaluate", response_model=FullSiteAssessmentResponse)
def evaluate_and_estimate_site(payload: FullSiteAssessmentRequest):
    """
    Evaluates site suitability across 5 core categories, generates an overall 0-100 score,
    and estimates the annual energy production (MWh) for Solar, Wind, or Hybrid configurations.
    """
    try:
        # 1. Run Category & Overall Site Scoring
        evaluation_result = scorer.evaluate_site(payload.site_metrics)

        # 2. Build Energy Request
        estimation_req = EnergyEstimationRequest(
            site_id=payload.site_metrics.site_id,
            technology=payload.technology,
            solar_capacity_mw=payload.solar_capacity_mw,
            wind_capacity_mw=payload.wind_capacity_mw,
            solar_capacity_factor=payload.solar_capacity_factor,
            wind_capacity_factor=payload.wind_capacity_factor
        )

        # 3. Compute Energy Yield Output
        yield_result = estimator.calculate_energy_yield(estimation_req)

        return FullSiteAssessmentResponse(
            evaluation=evaluation_result,
            energy_yield=yield_result
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error evaluating site metrics: {str(e)}"
        )


@router.post("/rank-sites")
def rank_candidate_sites(sites: list[SiteMetrics]):
    """
    Accepts multiple candidate site metric profiles and returns them sorted by overall score.
    """
    if not sites:
        raise HTTPException(status_code=400, detail="Site list cannot be empty.")
    
    ranked_results = scorer.rank_sites(sites)
    return {
        "total_sites_evaluated": len(ranked_results),
        "top_recommended_site": ranked_results[0].site_id,
        "rankings": ranked_results
    }