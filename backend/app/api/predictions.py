from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
import pandas as pd

# Existing Evaluation & Service imports
from app.evaluation.scorer import SiteScorer, SiteMetrics, SiteEvaluationResult
from app.services.energy_estimator import (
    EnergyEstimationService, 
    EnergyEstimationRequest, 
    EnergyEstimationResult, 
    DeploymentType
)

# Pipeline Integration imports
from app.services.analysis_pipeline import (
    AnalysisPipeline, 
    SiteAnalysisRequest, 
    ConsolidatedAnalysisResponse
)

# ML Forecasting Service import
from app.services.forecasting.forecast_service import ForecastingService

# Standardized Schemas for Tasks 1 & 2
from app.schemas.site import StandardizedSiteAssessmentRequest, StandardizedFinalResponse

router = APIRouter()

# Initialize Services
scorer = SiteScorer()
estimator = EnergyEstimationService()
pipeline = AnalysisPipeline()
forecasting_service = ForecastingService()


# ------------------------------------------------------------------------------
# EXISTING REQUEST / RESPONSE SCHEMAS (Preserved)
# ------------------------------------------------------------------------------

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


class ForecastExecutionRequest(BaseModel):
    deployment_type: str = Field(..., description="solar, wind, or hybrid")
    env_features: Dict[str, Any] = Field(
        default={
            "solar_irradiance": 5.5,
            "wind_speed": 8.0,
            "slope": 5.0
        },
        description="Environmental parameters like solar irradiance, wind speed, slope"
    )
    time_series_data: Optional[List[Dict[str, Any]]] = Field(
        default=[],
        description="List of records containing date or temporal features (month, day_of_year, is_weekend)"
    )


class ForecastExecutionResponse(BaseModel):
    status: str
    data: Dict[str, Any]


# ------------------------------------------------------------------------------
# ENDPOINTS (Preserved + New Addition)
# ------------------------------------------------------------------------------

@router.post("/evaluate", response_model=FullSiteAssessmentResponse)
def evaluate_and_estimate_site(payload: FullSiteAssessmentRequest):
    """Evaluates site suitability across core categories and estimates annual energy production."""
    try:
        evaluation_result = scorer.evaluate_site(payload.site_metrics)

        estimation_req = EnergyEstimationRequest(
            site_id=payload.site_metrics.site_id,
            technology=payload.technology,
            solar_capacity_mw=payload.solar_capacity_mw,
            wind_capacity_mw=payload.wind_capacity_mw,
            solar_capacity_factor=payload.solar_capacity_factor,
            wind_capacity_factor=payload.wind_capacity_factor
        )

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
    """Accepts multiple candidate site metric profiles and returns them sorted by score."""
    if not sites:
        raise HTTPException(status_code=400, detail="Site list cannot be empty.")
    
    ranked_results = scorer.rank_sites(sites)
    return {
        "total_sites_evaluated": len(ranked_results),
        "top_recommended_site": ranked_results[0].site_id,
        "rankings": ranked_results
    }


@router.post("/analysis", response_model=ConsolidatedAnalysisResponse, status_code=status.HTTP_200_OK)
def analyze_site(request: SiteAnalysisRequest):
    """Executes the complete unified suitability & yield pipeline."""
    try:
        return pipeline.run(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis pipeline execution failed: {str(e)}"
        )


@router.post("/forecast", response_model=ForecastExecutionResponse, status_code=status.HTTP_200_OK)
def execute_ml_forecast(payload: ForecastExecutionRequest):
    """Generates ML-driven energy forecasts utilizing the trained RandomForest model."""
    try:
        if payload.time_series_data and len(payload.time_series_data) > 0:
            df = pd.DataFrame(payload.time_series_data)
        else:
            df = pd.DataFrame([{}])

        forecast_result = forecasting_service.run_forecast(
            deployment_type=payload.deployment_type,
            time_series_df=df,
            env_features=payload.env_features
        )

        return ForecastExecutionResponse(
            status="success",
            data=forecast_result
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ML Forecasting failed: {str(e)}"
        )


@router.post("/full-analysis", response_model=StandardizedFinalResponse, status_code=status.HTTP_200_OK)
def execute_full_standardized_analysis(payload: StandardizedSiteAssessmentRequest):
    """
    NEW STANDARDIZED ENDPOINT (Tasks 1 & 2)
    Executes complete end-to-end flow returning a standardized response model.
    """
    try:
        return pipeline.run_full_analysis(payload)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Standardized pipeline execution failed: {str(e)}"
        )