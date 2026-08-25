class OSMClient:
    """
    Client for accessing OpenStreetMap infrastructure data.
    """

    def get_infrastructure_data(self, bounding_box: tuple) -> dict:
        """
        Inputs:
            bounding_box (tuple)

        Returns:
            dict containing roads, substations, transmission lines, etc.

        Possible failures:
            - Invalid bounding box
            - Network error
            - No infrastructure found
        """
        pass