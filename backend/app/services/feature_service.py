from app.data_sources.nasa_power import NASAPowerClient
from app.data_sources.global_wind_atlas import GlobalWindAtlasClient
from app.data_sources.srtm import SRTMClient
from app.data_sources.osm import OSMClient


class FeatureService:
    def __init__(self):
        self.nasa = NASAPowerClient()
        self.wind = GlobalWindAtlasClient()
        self.srtm = SRTMClient()
        self.osm = OSMClient()

    def collect_features(self, latitude: float, longitude: float):
        """
        Future feature engineering will collect data
        from all dataset clients.
        """

        solar = self.nasa.get_solar_data(latitude, longitude)
        wind = self.wind.get_wind_data(latitude, longitude)
        elevation = self.srtm.get_elevation(latitude, longitude)
        infrastructure = self.osm.get_nearby_infrastructure(latitude, longitude)

        return {
            "solar": solar,
            "wind": wind,
            "elevation": elevation,
            "infrastructure": infrastructure
        }