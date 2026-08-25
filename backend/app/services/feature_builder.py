from app.data_sources.nasa_power import NASAPowerClient
from app.data_sources.global_wind_atlas import GlobalWindAtlasClient
from app.data_sources.srtm import SRTMClient
from app.data_sources.osm import OSMClient


class FeatureBuilder:
    def __init__(self):
        self.nasa = NASAPowerClient()
        self.wind = GlobalWindAtlasClient()
        self.srtm = SRTMClient()
        self.osm = OSMClient()

    def build_features(self, latitude: float, longitude: float):
        """
        Placeholder integration point.
        Actual retrieval logic will be implemented later.
        """

        solar_data = self.nasa.get_solar_data(latitude, longitude)
        wind_data = self.wind.get_wind_data(latitude, longitude)
        elevation = self.srtm.get_elevation(latitude, longitude)
        infrastructure = self.osm.get_nearby_infrastructure(
            latitude,
            longitude,
            radius=5000
        )

        return {
            "solar": solar_data,
            "wind": wind_data,
            "elevation": elevation,
            "infrastructure": infrastructure
        }