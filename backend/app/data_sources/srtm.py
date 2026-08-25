class SRTMClient:
    """
    Client for accessing SRTM elevation dataset.
    """

    def get_elevation_data(self, latitude: float, longitude: float) -> dict:
        """
        Inputs:
            latitude (float)
            longitude (float)

        Returns:
            dict containing elevation and terrain information.

        Possible failures:
            - Invalid coordinates
            - Missing elevation data
        """
        pass