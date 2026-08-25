import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

def fetch_elevation(latitude: float, longitude: float) -> dict:
    """
    Fetch elevation data from Open-Meteo Elevation API (SRTM-grounded).
    Timeout is set to 30.0 seconds with 2 retries.
    """
    url = "https://api.open-meteo.com/v1/elevation"
    params = {
        "latitude": latitude,
        "longitude": longitude
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
