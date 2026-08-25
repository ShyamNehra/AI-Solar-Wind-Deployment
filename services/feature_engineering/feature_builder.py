from app.data_sources.nasa_power import NASAPowerClient
from app.data_sources.global_wind_atlas import GlobalWindAtlasClient
from app.data_sources.srtm import SRTMClient
from app.data_sources.osm import OSMClient


class FeatureBuilder:
    """
    Builder class responsible for coordinating dataset clients to assemble feature profiles.
    """

    def __init__(
        self,
        nasa_client: NASAPowerClient,
        wind_client: GlobalWindAtlasClient,
        terrain_client: SRTMClient,
        osm_client: OSMClient
    ):
        """
        Initialize the FeatureBuilder with all required dataset clients.

        Args:
            nasa_client (NASAPowerClient): Injected NASA POWER client.
            wind_client (GlobalWindAtlasClient): Injected Global Wind Atlas client.
            terrain_client (SRTMClient): Injected SRTM terrain client.
            osm_client (OSMClient): Injected OSM infrastructure client.
        """
        self._nasa_client = nasa_client
        self._wind_client = wind_client
        self._terrain_client = terrain_client
        self._osm_client = osm_client

    def build_features(
        self,
        latitude: float,
        longitude: float
    ) -> None:
        """
        Fetch dataset attributes and assemble them for the specified coordinates.

        Args:
            latitude (float): Latitude coordinate.
            longitude (float): Longitude coordinate.

        Raises:
            NotImplementedError: Always raised since feature aggregation is planned for a future milestone.
        """
        solar_data = self._nasa_client.get_solar_data(
            latitude,
            longitude
        )

        wind_data = self._wind_client.get_wind_data(
            latitude,
            longitude
        )

        terrain_data = self._terrain_client.get_terrain_data(
            latitude,
            longitude
        )

        infrastructure_data = self._osm_client.get_infrastructure_data(
            latitude,
            longitude
        )

        raise NotImplementedError(
            "Feature aggregation will be implemented in a future milestone."
        )
