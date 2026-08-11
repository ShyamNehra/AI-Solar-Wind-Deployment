from typing import Dict, Any, List, Optional
import pandas as pd
from pydantic import BaseModel, Field

from app.data_sources.nasa_power import NASAPowerClient
from app.evaluation.scorer import SiteScorer, SiteMetrics, SiteEvaluationResult
from app.services.energy_estimator import (
    EnergyEstimationService,
    EnergyEstimationRequest,
    EnergyEstimationResult,
    DeploymentType
)

# --- FORECASTING & FINANCIAL IMPORTS ---
from app.services.forecasting.data_loader import TimeSeriesDataLoader
from app.services.forecasting.feature_extraction import TemporalFeatureExtractor
from app.services.forecasting.forecast_service import ForecastingService
from app.evaluation.financial_analysis_service import FinancialAnalysisService
from app.schemas.site import StandardizedSiteAssessmentRequest, StandardizedFinalResponse, SiteCoordinates


# ------------------------------------------------------------------------------
# 1. PIPELINE INPUT / OUTPUT SCHEMAS (Preserved)
# ------------------------------------------------------------------------------

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
    electricity_tariff: float = Field(default=4.50, gt=0.0)


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
    forecasting: Dict[str, Any] = Field(default_factory=dict)
    financial_analysis: Dict[str, Any] = Field(default_factory=dict)  # Added financial field


# ------------------------------------------------------------------------------
# 2. PIPELINE ORCHESTRATOR SERVICE
# ------------------------------------------------------------------------------

class AnalysisPipeline:
    def __init__(self, nasa_client: Optional[NASAPowerClient] = None):
        self.scorer = SiteScorer()
        self.estimator = EnergyEstimationService()
        self.forecaster = ForecastingService()
        self.financial_service = FinancialAnalysisService()
        self.nasa_client = nasa_client or NASAPowerClient()

    def run(self, request: SiteAnalysisRequest) -> ConsolidatedAnalysisResponse:
        """Existing pipeline workflow preserved."""
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

        # Step 3: Evaluate Site & Calculate Site Score
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

        # Step 4: Estimate Energy Yield
        estimation_req = EnergyEstimationRequest(
            site_id=request.site_id,
            deployment_type=request.technology,
            solar_capacity_mw=request.solar_capacity_mw,
            wind_capacity_mw=request.wind_capacity_mw,
            solar_capacity_factor=0.20,
            wind_capacity_factor=0.35
        )
        energy_result = self.estimator.estimate_energy(estimation_req)

        # Step 5: Generate Deployment Recommendation
        recommendation = self._generate_recommendation(
            request=request, 
            score=evaluation_result.overall_score, 
            annual_mwh=energy_result.total_annual_mwh
        )

        # Step 6: Forecasting Pipeline Execution
        try:
            raw_historical_data = self.nasa_client.get_daily_data(
                latitude=request.latitude, 
                longitude=request.longitude
            )
            data_loader = TimeSeriesDataLoader(raw_historical_data)
            clean_time_series = data_loader.load_clean_data(date_column="date")
            time_featured_df = TemporalFeatureExtractor.extract_time_features(
                df=clean_time_series, 
                date_column="date"
            )
        except Exception:
            time_featured_df = pd.DataFrame()

        env_features = {
            "solar_irradiance": request.solar_irradiance,
            "wind_speed": request.wind_speed,
            "slope": request.slope,
            "electricity_tariff": getattr(request, "electricity_tariff", 4.50),
            "installed_capacity_mw": request.solar_capacity_mw + request.wind_capacity_mw
        }
        
        deployment_str = recommendation.recommended_technology.value if hasattr(recommendation.recommended_technology, 'value') else str(recommendation.recommended_technology)
        forecast_result = self.forecaster.run_forecast(
            deployment_type=deployment_str,
            time_series_df=time_featured_df,
            env_features=env_features
        )

        # Step 7: Calculate Financial Metrics
        net_yield_mwh = forecast_result.get("annual_energy_yield", {}).get("annual_net_yield_mwh", energy_result.total_annual_mwh)
        financial_result = self.financial_service.run_financial_analysis(
            deployment_type=deployment_str,
            annual_energy_yield_mwh=net_yield_mwh,
            env_features=env_features
        )

        # Step 8: Consolidated Output
        return ConsolidatedAnalysisResponse(
            site_id=request.site_id,
            coordinates={"latitude": request.latitude, "longitude": request.longitude},
            solar_assessment=solar_data,
            wind_assessment=wind_data,
            site_evaluation=evaluation_result,
            energy_yield=energy_result,
            deployment_recommendation=recommendation,
            forecasting=forecast_result,
            financial_analysis=financial_result
        )

    def run_full_analysis(self, request: StandardizedSiteAssessmentRequest) -> StandardizedFinalResponse:
        """
        NEW MANDATORY INTEGRATED WORKFLOW (Task 1 & Task 2)
        Location -> Env Data -> Solar/Wind -> ML -> Feasibility -> Yield -> Financials -> Recommendation
        """
        # Environmental Data Collection
        try:
            raw_historical_data = self.nasa_client.get_daily_data(latitude=request.latitude, longitude=request.longitude)
            solar_irr = float(raw_historical_data.get("solar_irradiance", request.solar_irradiance))
            wind_spd = float(raw_historical_data.get("wind_speed", request.wind_speed))
        except Exception:
            solar_irr = request.solar_irradiance
            wind_spd = request.wind_speed

        env_features = {
            "solar_irradiance": solar_irr,
            "wind_speed": wind_spd,
            "slope": request.slope,
            "distance_to_grid": request.distance_to_grid,
            "env_sensitivity": request.env_sensitivity,
            "installed_capacity_mw": request.solar_capacity_mw + request.wind_capacity_mw,
            "electricity_tariff": request.electricity_tariff
        }

        # Solar & Wind Assessment
        if solar_irr >= 5.0 and wind_spd >= 5.5:
            deployment_type = "hybrid"
        elif solar_irr > 5.0:
            deployment_type = "solar"
        else:
            deployment_type = "wind"

        # Execute ML Prediction, Feasibility, Yield, and Financial Pipeline
        forecast_result = self.forecaster.run_forecast(
            deployment_type=deployment_type,
            time_series_df=pd.DataFrame(),
            env_features=env_features
        )

        feasibility = forecast_result.get("feasibility_analysis", {})
        yield_data = forecast_result.get("annual_energy_yield", {})
        financials = forecast_result.get("financial_analysis", {})
        ml_pred = forecast_result.get("ml_prediction", {})

        # Final Recommendation synthesis
        is_feasible = feasibility.get("is_technically_feasible", True)
        payback = financials.get("payback_period_years", 0.0)

        if not is_feasible:
            reasoning = "Site rejected due to critical technical or environmental constraint violations."
        elif payback < 8.0:
            reasoning = f"Highly viable site for {deployment_type.upper()} deployment with strong ROI and {payback}-year payback."
        else:
            reasoning = f"Technically viable for {deployment_type.upper()} deployment, with a moderate payback period of {payback} years."

        return StandardizedFinalResponse(
            site_id=request.site_id,
            coordinates=SiteCoordinates(latitude=request.latitude, longitude=request.longitude),
            site_suitability={
                "solar_irradiance_kwh_m2": solar_irr,
                "wind_speed_m_s": wind_spd,
                "terrain_slope_deg": request.slope
            },
            recommended_deployment=deployment_type.capitalize(),
            technical_feasibility=feasibility,
            ml_prediction=ml_pred,
            energy_yield=yield_data,
            financial_metrics=financials,
            recommendation_reasoning=reasoning
        )

    def _generate_recommendation(
        self, request: SiteAnalysisRequest, score: float, annual_mwh: float
    ) -> DeploymentRecommendation:
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