from app.data_sources.nasa_power import NASAPowerClient
from app.data_sources.global_wind_atlas import GlobalWindAtlasClient
from services.feature_engineering.solar import SolarFeatureEngineer
from services.feature_engineering.wind import WindFeatureEngineer
from app.services.scoring_engine import evaluate_site_suitability
from app.services.deployment_strategy import recommend_deployment
from schemas.analysis import AnalysisRequest
from app.services.prediction_service import PredictionService
from app.services.feasibility_engine import TechnicalFeasibilityEngine
from app.services.energy_yield_service import EnergyYieldService
from app.services.financial_analysis_service import FinancialAnalysisService

class AnalysisPipelineService:
    """
    Service responsible for executing the complete site analysis workflow:
    Retrieving features, scoring the site, predicting with ML, checking feasibility, estimating yields, and evaluating financials.
    """

    def __init__(
        self,
        nasa_client: NASAPowerClient | None = None,
        wind_client: GlobalWindAtlasClient | None = None,
        prediction_service: PredictionService | None = None,
        feasibility_engine: TechnicalFeasibilityEngine | None = None,
        energy_yield_service: EnergyYieldService | None = None,
        financial_analysis_service: FinancialAnalysisService | None = None
    ):
        """
        Initialize the AnalysisPipelineService with injected or default clients/services.
        """
        self._nasa_client = nasa_client or NASAPowerClient()
        self._wind_client = wind_client or GlobalWindAtlasClient()
        self._solar_engineer = SolarFeatureEngineer(nasa_client=self._nasa_client)
        self._wind_engineer = WindFeatureEngineer(wind_client=self._wind_client)
        
        self._prediction_service = prediction_service or PredictionService()
        self._feasibility_engine = feasibility_engine or TechnicalFeasibilityEngine()
        self._energy_yield_service = energy_yield_service or EnergyYieldService()
        self._financial_analysis_service = financial_analysis_service or FinancialAnalysisService()

    def run_analysis(self, request: AnalysisRequest) -> dict:
        """
        Execute the complete site analysis workflow:
        1. Coordinate boundary validation
        2. Retrieve solar features using the existing Solar Feature Module
        3. Retrieve wind features using the existing Wind Feature Module (with fallback)
        4. Evaluate the site using the existing Site Scoring Engine
        5. Generate the deployment recommendation using the existing Deployment Recommendation Module
        6. Predict the site metrics using the ML models (Inference)
        7. Evaluate hard and soft constraints using the Technical Feasibility Engine
        8. Estimate energy yields using the Energy Yield Service
        9. Perform financial evaluations using the Financial Analysis Service
        10. Return consolidated analysis response
        """
        latitude = request.latitude
        longitude = request.longitude

        # 1. Coordinate boundary validation
        if not (-90.0 <= latitude <= 90.0):
            raise ValueError("Latitude must be between -90.0 and 90.0 degrees.")
        if not (-180.0 <= longitude <= 180.0):
            raise ValueError("Longitude must be between -180.0 and 180.0 degrees.")

        # 2. Retrieve solar features using the existing Solar Feature Module
        solar_data = self._solar_engineer.get_solar_features(latitude, longitude)

        # 3. Retrieve wind features using the existing Wind Feature Module
        wind_data = self._wind_engineer.get_wind_features(latitude, longitude)

        # 4. Prepare site suitability evaluation input data
        site_data = {
            "solar_irradiance": solar_data["solar_irradiance"],
            "wind_speed": wind_data["wind_speed"],
            "temperature": solar_data["temperature"],
            "humidity": solar_data["humidity"],
            "elevation": request.elevation,
            "slope": request.slope,
            "distance_to_road": request.distance_to_road,
            "distance_to_grid": request.distance_to_grid,
            "protected_area_distance": request.protected_area_distance,
            "environmental_impact_level": request.environmental_impact_level,
            "land_cost_per_acre": request.land_cost_per_acre,
            "grid_connection_cost": request.grid_connection_cost
        }

        # 5. Calculate the site score using the existing Site Scoring Engine
        suitability_result = evaluate_site_suitability(site_data)

        # 6. Generate the deployment recommendation using the existing Deployment Recommendation Module
        recommendation_result = recommend_deployment(
            solar_irradiance=solar_data["solar_irradiance"],
            wind_speed=wind_data["wind_speed"]
        )

        # 7. Predict site suitability score and technology deployment using ML
        predicted_score = None
        predicted_rec = None
        top_features = None
        explanation = None

        if self._prediction_service.models_loaded:
            predicted_score = self._prediction_service.predict_suitability_score(site_data)
            predicted_rec = self._prediction_service.predict_deployment_recommendation(site_data)
            top_features = self._prediction_service.get_feature_importance_regressor()
            explanation = f"Prediction is primarily influenced by {top_features[0]['feature']} and {top_features[1]['feature']}."

        # 8. Evaluate Technical Feasibility Constraints
        feasibility_res = self._feasibility_engine.evaluate_site(site_data)

        # 9. Estimate Energy Yields
        solar_yield = self._energy_yield_service.estimate_solar_energy_yield(
            solar_irradiance=solar_data["solar_irradiance"],
            installed_capacity_kw=request.installed_capacity_kw,
            system_efficiency=request.solar_system_efficiency,
            solar_capacity_factor=request.solar_capacity_factor
        )

        wind_yield = self._energy_yield_service.estimate_wind_energy_yield(
            wind_speed=wind_data["wind_speed"],
            installed_capacity_kw=request.installed_capacity_kw,
            wind_capacity_factor=request.wind_capacity_factor,
            losses=request.wind_operational_losses
        )

        hybrid_yield = self._energy_yield_service.estimate_hybrid_energy_yield(
            solar_yield=solar_yield,
            wind_yield=wind_yield
        )

        # Determine annual energy yield for the recommended technology
        rec_tech = recommendation_result["deployment"]
        if rec_tech == "Solar":
            recommended_yield = solar_yield
        elif rec_tech == "Wind":
            recommended_yield = wind_yield
        elif rec_tech == "Hybrid":
            recommended_yield = hybrid_yield
        else:
            recommended_yield = 0.0

        # 10. Perform Financial Analysis
        annual_revenue = self._financial_analysis_service.estimate_annual_revenue(
            annual_energy_yield_kwh=recommended_yield,
            electricity_tariff_inr_per_kwh=request.electricity_tariff_inr_per_kwh
        )

        project_cost = self._financial_analysis_service.estimate_project_cost(
            installed_capacity_kw=request.installed_capacity_kw,
            cost_per_kw=request.cost_per_kw,
            additional_installation_percentage=request.additional_installation_percentage
        )

        payback = self._financial_analysis_service.calculate_payback_period(
            total_project_cost=project_cost,
            annual_revenue=annual_revenue
        )

        roi = self._financial_analysis_service.calculate_roi(
            annual_revenue=annual_revenue,
            total_project_cost=project_cost
        )

        # 11. Return consolidated analysis dictionary
        return {
            "project": {
                "project_name": request.project_name,
                "location": request.location,
                "latitude": latitude,
                "longitude": longitude
            },
            "solar_features": {
                "solar_irradiance": solar_data["solar_irradiance"],
                "temperature": solar_data["temperature"],
                "humidity": solar_data["humidity"]
            },
            "wind_features": {
                "wind_speed": wind_data["wind_speed"],
                "wind_direction": wind_data["wind_direction"],
                "wind_power_density": wind_data["wind_power_density"]
            },
            "site_evaluation": {
                "resource_score": suitability_result["resource_score"],
                "terrain_score": suitability_result["terrain_score"],
                "infrastructure_score": suitability_result["infrastructure_score"],
                "environmental_score": suitability_result["environmental_score"],
                "economic_score": suitability_result["economic_score"]
            },
            "site_score": {
                "overall_score": suitability_result["overall_score"]
            },
            "deployment_recommendation": recommendation_result,

            # ML Predictions
            "predicted_overall_score": predicted_score,
            "predicted_deployment": predicted_rec,
            "top_features": top_features,
            "explanation": explanation,

            # Feasibility Result
            "technical_feasibility": feasibility_res["technical_feasibility"],
            "technical_feasibility_score": feasibility_res["technical_feasibility_score"],
            "constraint_violations": feasibility_res["constraint_violations"],
            "critical_violations": feasibility_res["critical_violations"],
            "overall_status": feasibility_res["overall_status"],

            # Energy Yield Estimation
            "solar_energy_yield_kwh": solar_yield,
            "wind_energy_yield_kwh": wind_yield,
            "hybrid_energy_yield_kwh": hybrid_yield,
            "recommended_annual_energy_kwh": recommended_yield,

            # Financial Analysis
            "annual_revenue": annual_revenue,
            "estimated_project_cost": project_cost,
            "payback_period": payback,
            "roi": roi
        }
