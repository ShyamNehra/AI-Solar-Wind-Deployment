class GlobalWindAtlasClient:
    """
    Client for accessing Global Wind Atlas dataset.
    """

    def get_wind_data(self, latitude: float, longitude: float) -> dict:
        """
        Inputs:
            latitude (float)
            longitude (float)

        Returns:
            dict containing wind information.

        Possible failures:
            - Invalid coordinates
            - Network error
            - No data available
        """
        pass