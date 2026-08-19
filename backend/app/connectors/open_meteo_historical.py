import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

def fetch_historical_wind_data(latitude: float, longitude: float) -> dict:
    """
    Fetch historical wind speed and direction hourly time-series data from Open-Meteo Archive API.
    Retrieves full calendar year 2025 data to calculate a stable average climatology.
    Timeout is set to 30.0 seconds with 2 retries on standard server errors.
    """
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": "2025-01-01",
        "end_date": "2025-12-31",
        "hourly": "wind_speed_10m,wind_direction_10m",
        "wind_speed_unit": "ms"
    }
    
    session = requests.Session()
    retries = Retry(
        total=2, 
        backoff_factor=0.5, 
        status_forcelist=[500, 502, 503, 504]
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))
    
    response = session.get(url, params=params, timeout=30.0)
    response.raise_for_status()
    return response.json()
