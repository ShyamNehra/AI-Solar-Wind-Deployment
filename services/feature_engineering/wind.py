from app.data_sources.global_wind_atlas import GlobalWindAtlasClient


class WindFeatureEngineer:
    """
    Service responsible for engineering wind resource features using the Global Wind Atlas client.
    """

    def __init__(self, wind_client: GlobalWindAtlasClient):
        """
        Initialize the WindFeatureEngineer with a GlobalWindAtlasClient.

        Args:
            wind_client (GlobalWindAtlasClient): The injected client for Global Wind Atlas dataset.
        """
        self._wind_client = wind_client
