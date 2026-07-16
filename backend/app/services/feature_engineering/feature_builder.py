from app.data_sources.nasa_power import NASAPowerClient
from app.data_sources.global_wind_atlas import GlobalWindAtlasClient
from app.data_sources.srtm import SRTMClient
from app.data_sources.osm import OpenStreetMapClient

# Import your brand-new localized services
from app.services.feature_engineering.solar import SolarService
from app.services.feature_engineering.wind import WindService
from app.services.feature_engineering.terrain import TerrainService
from app.services.feature_engineering.infrastructure import InfraService

class FeatureBuilder:
    """Orchestrates specific underlying micro-services to generate a complete site profile."""
    
    def __init__(self):
        # 1. Initialize the low-level data clients
        nasa_client = NASAPowerClient()
        wind_client = GlobalWindAtlasClient()
        srtm_client = SRTMClient()
        osm_client = OpenStreetMapClient()
        
        # 2. Inject them into your dedicated feature services
        self.solar_service = SolarService(nasa_client)
        self.wind_service = WindService(wind_client)
        self.terrain_service = TerrainService(srtm_client)
        self.infra_service = InfraService(osm_client)

    def build_environmental_profile(self, latitude: float, longitude: float) -> dict:
        """Gathers calculations from all services to assemble a master intelligence vector."""
        
        return {
            "metadata": {"latitude": latitude, "longitude": longitude},
            "solar_features": self.solar_service.calculate_solar_potential(latitude, longitude),
            "wind_features": self.wind_service.estimate_wind_resource(latitude, longitude),
            "terrain_features": self.terrain_service.evaluate_topography(latitude, longitude),
            "infrastructure_features": self.infra_service.evaluate_proximity_constraints(latitude, longitude),
            "status": "Feature Layer Architecture Complete"
        }