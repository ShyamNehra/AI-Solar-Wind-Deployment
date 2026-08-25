import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

def fetch_solar_data(latitude: float, longitude: float) -> dict:
    """
    Fetch solar irradiance and temperature climatology data from NASA POWER API.
    Timeout is set to 30.0 seconds with 2 retries on standard server errors.
    """
    url = "https://power.larc.nasa.gov/api/temporal/climatology/point"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "parameters": "ALLSKY_SFC_SW_DWN,T2M",
        "community": "RE",
        "format": "JSON"
    }
    
    session = requests.Session()
    # Retries = 2 (total=2)
    retries = Retry(
        total=2, 
        backoff_factor=0.5, 
        status_forcelist=[500, 502, 503, 504]
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))
    
    response = session.get(url, params=params, timeout=30.0)
    response.raise_for_status()
    return response.json()

def get_monthly_solar_irradiance(payload: dict) -> dict:
    """
    Extract the 12 monthly solar irradiance (ALLSKY_SFC_SW_DWN) values from the NASA POWER payload.
    """
    param = payload["properties"]["parameter"]["ALLSKY_SFC_SW_DWN"]
    months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    return {m: param[m] for m in months}
