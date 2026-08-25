from app.data_sources.srtm import SRTMClient


class TerrainFeatureEngineer:
    """
    Service responsible for engineering terrain elevation features using the SRTM client.
    """

    def __init__(self, terrain_client: SRTMClient):
        """
        Initialize the TerrainFeatureEngineer with a SRTMClient.

        Args:
            terrain_client (SRTMClient): The injected client for SRTM dataset.
        """
        self._terrain_client = terrain_client
