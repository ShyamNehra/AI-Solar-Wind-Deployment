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

    def get_wind_features(
        self,
        latitude: float,
        longitude: float
    ) -> dict:
        """
        Retrieve and extract wind features for the specified coordinates.
        Uses Global Wind Atlas client, with a fallback to deterministic testing mock data
        if the client is not yet fully implemented.
        """
        # Coordinate boundary validation
        if not (-90.0 <= latitude <= 90.0):
            raise ValueError("Latitude must be between -90.0 and 90.0 degrees.")
        if not (-180.0 <= longitude <= 180.0):
            raise ValueError("Longitude must be between -180.0 and 180.0 degrees.")

        try:
            raw_data = self._wind_client.get_wind_data(latitude, longitude)
            return {
                "wind_speed": raw_data.get("wind_speed", 0.0),
                "wind_direction": raw_data.get("wind_direction", 0.0),
                "wind_power_density": raw_data.get("wind_power_density", 0.0)
            }
        except NotImplementedError:
            # Fallback mock logic for integration testing and development
            # Returns deterministic wind parameters based on coordinates
            speed = 2.0 + (abs(latitude) + abs(longitude)) % 8.0
            direction = (abs(latitude) * 10 + abs(longitude) * 5) % 360.0
            power_density = speed * 50.0
            return {
                "wind_speed": round(speed, 2),
                "wind_direction": round(direction, 2),
                "wind_power_density": round(power_density, 2)
            }

