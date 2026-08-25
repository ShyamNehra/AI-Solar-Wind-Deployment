import urllib.request
import urllib.parse
import json
import socket
import urllib.error

# Named constant for the NASA POWER API climatology point endpoint
NASA_POWER_BASE_URL = "https://power.larc.nasa.gov/api/temporal/climatology/point"


class NASAPowerClient:
    """
    Client for interacting with the NASA POWER API to retrieve solar resource data.
    """

    def get_solar_data(
        self,
        latitude: float,
        longitude: float
    ) -> dict:
        """
        Retrieve solar resource data for a given geographical coordinate.

        Purpose:
            Fetch meteorological and solar parameter values from NASA POWER dataset.

        Required inputs:
            latitude (float): Latitude coordinate in decimal degrees.
            longitude (float): Longitude coordinate in decimal degrees.

        Expected output:
            dict: Solar resource data containing daily solar irradiance, temperature, etc.

        Possible failure conditions:
            - ValueError: If coordinates are out of valid bounds.
            - ConnectionError: If network connection to NASA POWER service fails.
            - RuntimeError: If dataset is unavailable or returns an error.
            - TimeoutError: If the request to the external API times out.
        """
        # Coordinate boundary validation
        if not (-90.0 <= latitude <= 90.0):
            raise ValueError("Latitude must be between -90.0 and 90.0 degrees.")
        if not (-180.0 <= longitude <= 180.0):
            raise ValueError("Longitude must be between -180.0 and 180.0 degrees.")

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "parameters": "ALLSKY_SFC_SW_DWN,T2M,RH2M",
            "community": "RE",
            "format": "JSON"
        }

        query_string = urllib.parse.urlencode(params)
        full_url = f"{NASA_POWER_BASE_URL}?{query_string}"

        req = urllib.request.Request(
            full_url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    return json.loads(response.read().decode('utf-8'))
                else:
                    raise RuntimeError(
                        f"NASA POWER API returned status code {response.status}"
                    )
        except socket.timeout as e:
            raise TimeoutError(f"Request to NASA POWER API timed out: {e}")
        except urllib.error.HTTPError as e:
            raise RuntimeError(
                f"NASA POWER API HTTP Error: {e.code} {e.reason}"
            )
        except urllib.error.URLError as e:
            raise ConnectionError(
                f"Failed to connect to NASA POWER API: {e.reason}"
            )
        except Exception as e:
            raise RuntimeError(f"An unexpected error occurred: {e}")
