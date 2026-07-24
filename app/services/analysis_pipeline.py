from app.data_sources.nasa_power import NASAPowerClient
from app.data_sources.global_wind_atlas import GlobalWindAtlasClient
from services.feature_engineering.solar import SolarFeatureEngineer
from services.feature_engineering.wind import WindFeatureEngineer
from app.services.scoring_engine import evaluate_site_suitability
from app.services.deployment_strategy import recommend_deployment
from schemas.analysis import AnalysisRequest

class AnalysisPipelineService:
    """
    Service responsible for executing the complete site analysis workflow.
    """

    def __init__(
        self,
        nasa_client: NASAPowerClient | None = None,
        wind_client: GlobalWindAtlasClient | None = None
    ):
        """
        Initialize the AnalysisPipelineService with injected or default clients.
        """
        self._nasa_client = nasa_client or NASAPowerClient()
        self._wind_client = wind_client or GlobalWindAtlasClient()
        self._solar_engineer = SolarFeatureEngineer(nasa_client=self._nasa_client)
        self._wind_engineer = WindFeatureEngineer(wind_client=self._wind_client)

    def run_analysis(self, request: AnalysisRequest) -> dict:
        """
        Execute the complete site analysis workflow:
        1. Coordinate boundary validation
        2. Retrieve solar features using the existing Solar Feature Module
        3. Retrieve wind features using the existing Wind Feature Module (with fallback)
        4. Evaluate the site using the existing Site Scoring Engine
        5. Generate the deployment recommendation using the existing Deployment Recommendation Module
        6. Return one consolidated analysis object
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

        # 7. Return consolidated analysis dictionary
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
            "deployment_recommendation": recommendation_result
        }
