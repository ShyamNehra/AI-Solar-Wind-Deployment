class OSMClient:
    """
    Client for interacting with OpenStreetMap (OSM) Overpass API to retrieve nearby infrastructure data.
    """

    def get_infrastructure_data(
        self,
        latitude: float,
        longitude: float,
        radius: int = 5000
    ) -> dict:
        """
        Retrieve nearby infrastructure data within a specified search radius.

        Purpose:
            Query OpenStreetMap dataset for roads, buildings, power transmission lines, and substations.

        Required inputs:
            latitude (float): Latitude coordinate in decimal degrees.
            longitude (float): Longitude coordinate in decimal degrees.
            radius (int, optional): Search radius in meters. Defaults to 5000.

        Expected output:
            dict: Structures, distance, and counts of nearby infrastructure features.

        Possible failure conditions:
            - ConnectionError: If network connection to OpenStreetMap Overpass API fails.
            - ValueError: If coordinates are out of valid bounds or radius is negative.
            - LookupError: If no nearby infrastructure exists within the specified radius.
        """
        raise NotImplementedError()
