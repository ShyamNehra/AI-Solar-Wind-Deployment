from app.data_sources.osm import OSMClient


class InfrastructureFeatureEngineer:
    """
    Service responsible for engineering infrastructure features using the OSM client.
    """

    def __init__(self, osm_client: OSMClient):
        """
        Initialize the InfrastructureFeatureEngineer with an OSMClient.

        Args:
            osm_client (OSMClient): The injected client for OSM dataset.
        """
        self._osm_client = osm_client
