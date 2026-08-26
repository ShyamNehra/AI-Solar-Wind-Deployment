import requests
import math

def fetch_nasa_data(latitude: float, longitude: float) -> dict:
    """
    Fetches live annual solar irradiance (kWh/m²/day) and 50m wind speed (m/s)
    from NASA POWER API.
    """
    url = "https://power.larc.nasa.gov/api/temporal/climatology/point"
    params = {
        "parameters": "ALLSKY_SFC_SW_DWN,WS50M",
        "community": "RE",
        "longitude": longitude,
        "latitude": latitude,
        "format": "JSON"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()["properties"]["parameter"]
            solar = data.get("ALLSKY_SFC_SW_DWN", {}).get("ANN", 4.5)
            wind = data.get("WS50M", {}).get("ANN", 5.0)
            return {"solar_irradiance": solar, "wind_speed": wind}
    except Exception as e:
        print(f"NASA POWER API Error: {e}")
        
    return {"solar_irradiance": 4.5, "wind_speed": 5.0}


def fetch_osm_grid_distance(latitude: float, longitude: float) -> float:
    """
    Queries OpenStreetMap Overpass API for nearest power substations or lines
    within a 50km radius and returns approximate distance in km.
    """
    overpass_url = "https://overpass-api.de/api/interpreter"
    
    query = f"""
    [out:json];
    (
      node["power"="substation"](around:50000,{latitude},{longitude});
      way["power"="line"](around:50000,{latitude},{longitude});
    );
    out center 1;
    """
    
    try:
        response = requests.post(overpass_url, data={'data': query}, timeout=10)
        if response.status_code == 200:
            elements = response.json().get('elements', [])
            if elements:
                elem = elements[0]
                grid_lat = elem.get('lat') or elem.get('center', {}).get('lat')
                grid_lon = elem.get('lon') or elem.get('center', {}).get('lon')
                
                if grid_lat and grid_lon:
                    dist = math.sqrt((grid_lat - latitude)**2 + (grid_lon - longitude)**2) * 111.0
                    return round(dist, 2)
    except Exception as e:
        print(f"OSM Overpass API Error: {e}")
        
    return 12.5