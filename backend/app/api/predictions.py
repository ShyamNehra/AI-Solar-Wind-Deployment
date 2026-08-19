from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, status, Request
from sqlalchemy.orm import Session
from app.core.rate_limiter import limiter
from app.auth.dependencies import get_current_user
from pydantic import BaseModel, Field
import pandas as pd

from app.database.database import get_db
from app.models.project import Project
from app.models.site import Site
from app.services.persistence_service import PersistenceService

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
@limiter.limit("20/minute")
def execute_ml_forecast(request: Request, payload: ForecastExecutionRequest):
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
@limiter.limit("20/minute")
def execute_full_standardized_analysis(
    request: Request,
    payload: StandardizedSiteAssessmentRequest,
    db: Session = Depends(get_db)
):
    """
    Executes complete end-to-end data-driven flow returning a standardized response model
    and auto-persists evaluation records to DB tables (EnvironmentalData, Predictions, SuitabilityScore).
    """
    try:
        response = pipeline.run_full_analysis(payload)

        # Auto-persist analysis record to database tables in background safety block
        try:
            # 1. Fetch or create default Project
            org_id = getattr(payload, "organization_id", None) or "1001"
            project = db.query(Project).filter(Project.organization_id == org_id).first()
            if not project:
                project = Project(
                    project_name=f"Workspace Project ({org_id})",
                    description="Auto-generated workspace project container",
                    organization_id=org_id,
                    project_type="hybrid",
                    status="active"
                )
                db.add(project)
                db.commit()
                db.refresh(project)

            # 2. Fetch or create Site record
            lat = float(payload.latitude)
            lng = float(payload.longitude)
            site = db.query(Site).filter(Site.latitude == lat, Site.longitude == lng, Site.organization_id == org_id).first()
            tech_dict = response.technical_feasibility if isinstance(response.technical_feasibility, dict) else response.technical_feasibility.model_dump()
            suit_dict = response.site_suitability if isinstance(response.site_suitability, dict) else response.site_suitability.model_dump()

            if not site:
                site = Site(
                    project_id=project.id,
                    organization_id=org_id,
                    latitude=lat,
                    longitude=lng,
                    area_sq_meters=500000.0,
                    elevation_m=float(tech_dict.get("elevation_m", 250.0)),
                    region=suit_dict.get("region", "Evaluated Sector"),
                    land_ownership="Evaluated Parcel",
                    existing_infrastructure="Proximity Grid Analyzed"
                )
                db.add(site)
                db.commit()
                db.refresh(site)

            # 3. Persist EnvironmentalData
            suit_dict = response.site_suitability if isinstance(response.site_suitability, dict) else response.site_suitability.model_dump()
            yield_dict = response.energy_yield if isinstance(response.energy_yield, dict) else response.energy_yield.model_dump()

            PersistenceService.save_environmental_data(
                db=db,
                site_id=site.id,
                env_features={
                    "solar_irradiance": suit_dict.get("solar_irradiance_kwh_m2_day", 5.5),
                    "wind_speed": suit_dict.get("wind_speed_m_s", 6.0),
                    "slope": suit_dict.get("terrain_slope_deg", 3.0),
                    "temperature": suit_dict.get("temperature_c", 25.0),
                    "rainfall": suit_dict.get("rainfall_mm_year", 400.0),
                    "cloud_cover": suit_dict.get("cloud_cover_pct", 30.0),
                    "land_use_type": "Evaluated Open Parcel"
                },
                data_source="NASA_POWER"
            )

            # 4. Persist Solar & Wind Predictions
            solar_yield_kwh = yield_dict.get("annual_net_yield_mwh", 25000.0) * 1000.0
            apply_cf = yield_dict.get("applied_capacity_factor", 0.22)
            solar_ghi = suit_dict.get("solar_irradiance_kwh_m2_day", 5.5)

            PersistenceService.save_solar_prediction(
                db=db,
                site_id=site.id,
                solar_metrics={
                    "annual_irradiance": solar_ghi * 365.0,
                    "peak_sun_hours": solar_ghi,
                    "expected_energy_output_kwh": solar_yield_kwh,
                    "capacity_factor": apply_cf,
                    "performance_ratio": yield_dict.get("system_efficiency", 0.85)
                }
            )

            wind_speed = suit_dict.get("wind_speed_m_s", 6.0)
            wpd = suit_dict.get("wind_power_density_w_m2", 150.0)

            PersistenceService.save_wind_prediction(
                db=db,
                site_id=site.id,
                wind_metrics={
                    "average_wind_speed": wind_speed,
                    "wind_power_density": wpd,
                    "turbulence_intensity": suit_dict.get("turbulence_intensity_pct", 10.0) / 100.0,
                    "capacity_factor": apply_cf,
                    "expected_annual_energy_kwh": solar_yield_kwh * 0.4
                }
            )

            # 5. Persist SuitabilityScore
            overall_sc = suit_dict.get("overall_score", 85.0)
            category_str = "Excellent" if overall_sc >= 85 else ("Highly Suitable" if overall_sc >= 75 else "Moderately Suitable")

            PersistenceService.save_suitability_score(
                db=db,
                site_id=site.id,
                suitability_result={
                    "overall_score": overall_sc,
                    "category": category_str,
                    "sub_scores": {
                        "resource_score": min(100.0, overall_sc * 1.05),
                        "geographic_score": min(100.0, overall_sc * 0.98),
                        "infrastructure_score": min(100.0, overall_sc * 0.95),
                        "environmental_score": min(100.0, overall_sc * 0.97),
                        "economic_score": min(100.0, overall_sc * 1.02)
                    }
                }
            )
        except Exception as persist_err:
            print(f"[Warning] Background persistence warning: {persist_err}")

        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Standardized pipeline execution failed: {str(e)}"
        )