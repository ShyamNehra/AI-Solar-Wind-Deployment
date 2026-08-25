import math
import requests
import logging

logger = logging.getLogger(__name__)

# List of public Overpass API interpreter endpoints for load balancing / retry fallback
OVERPASS_API_URLS = [
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on the Earth's surface
    using the Haversine formula. Returns distance in kilometers.
    """
    R = 6371.0  # Earth's radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def fetch_infrastructure_proximity(lat: float, lon: float, radius_km: float = 10.0) -> dict:
    """
    Fetch proximity to roads, transmission lines/substations, urban areas, protected zones,
    and water bodies from OpenStreetMap using the Overpass API interpreter.
    Calculates distances in kilometers.
    """
    radius_m = radius_km * 1000.0
    
    # Overpass QL query targeting key infrastructure features
    query = f"""[out:json][timeout:30];
(
  way["highway"](around:{radius_m}, {lat}, {lon});
  node["power"](around:{radius_m}, {lat}, {lon});
  way["power"](around:{radius_m}, {lat}, {lon});
  node["place"](around:{radius_m}, {lat}, {lon});
  way["landuse"~"residential|commercial|industrial|retail"](around:{radius_m}, {lat}, {lon});
  way["boundary"="protected_area"](around:{radius_m}, {lat}, {lon});
  relation["boundary"="protected_area"](around:{radius_m}, {lat}, {lon});
  way["leisure"="nature_reserve"](around:{radius_m}, {lat}, {lon});
  relation["leisure"="nature_reserve"](around:{radius_m}, {lat}, {lon});
  way["natural"="water"](around:{radius_m}, {lat}, {lon});
  way["waterway"](around:{radius_m}, {lat}, {lon});
);
out geom;"""

    headers = {
        "User-Agent": "SolarWindDeploymentPlatform/1.0 (contact: info@solarwinddeployment.local)"
    }
    
    response_data = None
    last_error = None
    
    for url in OVERPASS_API_URLS:
        try:
            logger.info(f"Querying Overpass API at {url}...")
            response = requests.post(url, data=query, headers=headers, timeout=30)
            if response.status_code == 200:
                response_data = response.json()
                if "elements" in response_data:
                    break
            elif response.status_code == 429:
                logger.warning(f"Overpass API rate limited at {url}: 429")
                last_error = f"429 Rate Limit: {response.text}"
            else:
                logger.warning(f"Overpass API returned status {response.status_code} at {url}")
                last_error = f"Status {response.status_code}: {response.text}"
        except Exception as e:
            logger.warning(f"Connection failed for Overpass API at {url}: {e}")
            last_error = str(e)
            
    if not response_data or "elements" not in response_data:
        import os
        if os.getenv("ENVIRONMENT") == "development":
            logger.warning(f"Overpass API query failed or timed out: {last_error}. Falling back to default proximity values in development mode.")
            return {
                "nearest_road_km": 1.2,
                "nearest_substation_km": 4.5,
                "nearest_urban_area_km": 8.0,
                "nearest_protected_zone_km": None,
                "nearest_water_body_km": 3.1
            }
        raise RuntimeError(f"Overpass API query failed or timed out. Details: {last_error}")
        
    elements = response_data.get("elements", [])
    
    min_distances = {
        "nearest_road_km": None,
        "nearest_substation_km": None,
        "nearest_urban_area_km": None,
        "nearest_protected_zone_km": None,
        "nearest_water_body_km": None
    }
    
    for element in elements:
        tags = element.get("tags", {})
        elem_type = element.get("type")
        
        # Collect all points for this element
        points = []
        if elem_type == "node" and "lat" in element and "lon" in element:
            points.append((element["lat"], element["lon"]))
        elif "geometry" in element:
            for pt in element["geometry"]:
                if pt and "lat" in pt and "lon" in pt:
                    points.append((pt["lat"], pt["lon"]))
                    
        if not points:
            continue
            
        # Minimum distance from site point to this element
        dist = min(haversine_distance(lat, lon, pt_lat, pt_lon) for pt_lat, pt_lon in points)
        
        # Categorize by tags
        # 1. Road
        if "highway" in tags:
            if min_distances["nearest_road_km"] is None or dist < min_distances["nearest_road_km"]:
                min_distances["nearest_road_km"] = dist
                
        # 2. Power substation/transmission lines
        if "power" in tags:
            if min_distances["nearest_substation_km"] is None or dist < min_distances["nearest_substation_km"]:
                min_distances["nearest_substation_km"] = dist
                
        # 3. Urban Area
        if "place" in tags or tags.get("landuse") in ["residential", "commercial", "industrial", "retail"]:
            if min_distances["nearest_urban_area_km"] is None or dist < min_distances["nearest_urban_area_km"]:
                min_distances["nearest_urban_area_km"] = dist
                
        # 4. Protected Area
        if tags.get("boundary") == "protected_area" or tags.get("leisure") == "nature_reserve":
            if min_distances["nearest_protected_zone_km"] is None or dist < min_distances["nearest_protected_zone_km"]:
                min_distances["nearest_protected_zone_km"] = dist
                
        # 5. Water Body
        if tags.get("natural") == "water" or "waterway" in tags:
            if min_distances["nearest_water_body_km"] is None or dist < min_distances["nearest_water_body_km"]:
                min_distances["nearest_water_body_km"] = dist
                
    return min_distances
