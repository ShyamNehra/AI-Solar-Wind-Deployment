from app.data_sources.nasa_power import NasaPowerClient


class SolarFeatureService:
    """
    Service responsible for retrieving solar-related features.
    """

    def __init__(self):
        self.nasa_client = NasaPowerClient()

    def get_solar_features(self, latitude: float, longitude: float):
        """
        Fetch real environmental measurements
        from NASA POWER API.
        """

        return self.nasa_client.get_weather_data(
            latitude,
            longitude
        )