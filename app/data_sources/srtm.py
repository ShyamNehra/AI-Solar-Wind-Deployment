class SRTMClient:
    """
    Client for interacting with Shuttle Radar Topography Mission (SRTM) dataset to retrieve terrain elevation data.
    """

    def get_terrain_data(
        self,
        latitude: float,
        longitude: float
    ) -> dict:
        """
        Retrieve terrain elevation, slope, and aspect data for a given geographical coordinate.

        Purpose:
            Fetch elevation and topographic parameters from Shuttle Radar Topography Mission (SRTM) dataset.

        Required inputs:
            latitude (float): Latitude coordinate in decimal degrees.
            longitude (float): Longitude coordinate in decimal degrees.

        Expected output:
            dict: Topographic parameters including elevation in meters and slope/aspect percentages.

        Possible failure conditions:
            - KeyError: If terrain elevation data is missing for the given coordinates.
            - ValueError: If coordinates are out of valid bounds.
            - ConnectionError: If network connection to the elevation API service fails.
        """
        raise NotImplementedError()
