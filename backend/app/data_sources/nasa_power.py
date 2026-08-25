import requests


class NasaPowerClient:
    """
    Client for accessing the NASA POWER API.
    """

    BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"

    def get_weather_data(self, latitude: float, longitude: float):
        """
        Fetch solar and weather data from NASA POWER API.

        Inputs:
            latitude (float)
            longitude (float)

        Returns:
            dict containing:
                solar_irradiance
                temperature
                relative_humidity

        Returns an error dictionary if the request fails.
        """

        params = {
            "parameters": "ALLSKY_SFC_SW_DWN,T2M,RH2M",
            "community": "RE",
            "latitude": latitude,
            "longitude": longitude,
            "start": "20250101",
            "end": "20250101",
            "format": "JSON"
        }

        try:
            response = requests.get(
                self.BASE_URL,
                params=params,
                timeout=10
            )

            response.raise_for_status()

            data = response.json()

            parameters = data.get("properties", {}).get("parameter", {})

            return {
                "solar_irradiance": parameters.get("ALLSKY_SFC_SW_DWN", {}).get("20250101"),
                "temperature": parameters.get("T2M", {}).get("20250101"),
                "relative_humidity": parameters.get("RH2M", {}).get("20250101")
            }

        except requests.exceptions.RequestException as e:
            return {
                "error": str(e)
            }