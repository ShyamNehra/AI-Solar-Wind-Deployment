import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

def fetch_wind_data(latitude: float, longitude: float) -> dict:
    """
    Fetch wind resource data from Open-Meteo Wind API (climatology alternative).
    Timeout is set to 30.0 seconds with 2 retries.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "wind_speed_10m,wind_speed_80m,wind_direction_10m,wind_direction_80m"
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
