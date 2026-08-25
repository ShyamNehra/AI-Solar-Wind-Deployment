from app.data_sources.nasa_power import NASAPowerClient


class SolarFeatureEngineer:
    """
    Service responsible for engineering solar resource features using the NASA POWER client.
    """

    def __init__(self, nasa_client: NASAPowerClient):
        """
        Initialize the SolarFeatureEngineer with a NASAPowerClient.

        Args:
            nasa_client (NASAPowerClient): The injected client for NASA POWER dataset.
        """
        self._nasa_client = nasa_client

    def get_solar_features(
        self,
        latitude: float,
        longitude: float
    ) -> dict:
        """
        Retrieve and extract solar features for the specified coordinates using the NASA POWER client.

        Args:
            latitude (float): Coordinate latitude.
            longitude (float): Coordinate longitude.

        Returns:
            dict: Dictionary containing solar_irradiance, temperature, and humidity.
        """
        raw_data = self._nasa_client.get_solar_data(latitude, longitude)

        try:
            parameter_data = raw_data["properties"]["parameter"]
            solar_irradiance = parameter_data["ALLSKY_SFC_SW_DWN"]["ANN"]
            temperature = parameter_data["T2M"]["ANN"]
            humidity = parameter_data["RH2M"]["ANN"]

            # Check if coordinates have invalid data (NASA uses -999 for missing values)
            if solar_irradiance == -999 or temperature == -999 or humidity == -999:
                raise ValueError(
                    "Missing or invalid solar data for the specified coordinates."
                )

            return {
                "solar_irradiance": solar_irradiance,
                "temperature": temperature,
                "humidity": humidity
            }
        except KeyError as ke:
            raise KeyError(
                f"Required parameter was missing in NASA POWER response: {ke}"
            )
