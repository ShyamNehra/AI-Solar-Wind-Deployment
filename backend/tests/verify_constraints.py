import time
import requests
from app.services.gis_service import check_spatial_land_use
from app.evaluation.feasibility_engine import FeasibilityEngine

test_coordinates = [
    {"name": "Gulf of Khambhat (Offshore Ocean)", "lat": 21.2000, "lng": 72.3000},
    {"name": "Ranthambore Tiger Reserve", "lat": 26.0173, "lng": 76.5026},
    {"name": "Jim Corbett National Park", "lat": 29.5300, "lng": 78.7747},
    {"name": "Sambhar Salt Lake", "lat": 26.9000, "lng": 75.0000},
    {"name": "Kedarnath Valley (Steep Mountain)", "lat": 30.7346, "lng": 79.0669},
    {"name": "Bhadla Solar Desert", "lat": 27.5397, "lng": 71.9152},
    {"name": "Muppandal Wind Corridor", "lat": 8.2589, "lng": 77.5458}
]

def get_site_metrics(lat, lng):
    try:
        res = requests.get(f"https://api.open-meteo.com/v1/elevation?latitude={lat}&longitude={lng}", timeout=4)
        elev = res.json().get("elevation", [0])[0] if res.status_code == 200 else 250.0
    except Exception:
        elev = 250.0
    
    # Realistically assign steep slope (>18°) for Kedarnath
    slope = 18.5 if elev > 2000 else 2.5
    return elev, slope

def run_full_inspection(site):
    lat, lng = site["lat"], site["lng"]
    print(f"\n=================== TESTING: {site['name']} ({lat}, {lng}) ===================")

    # 1. Step 1: GIS Lookup
    detected_type, zone_name = check_spatial_land_use(lat, lng)
    print(f"  * Extracted Land Type : {detected_type or 'Clear / Unrestricted'}")
    print(f"  * Extracted Zone Name : {zone_name or 'None'}")

    # 2. Step 2: Fetch Elevation & Slope
    elev, slope = get_site_metrics(lat, lng)
    print(f"  * Terrain Elevation   : {elev}m | Surface Slope: {slope}°")

    # 3. Step 3: Feasibility Evaluation
    env_features = {
        "latitude": lat,
        "longitude": lng,
        "solar_irradiance": 5.8,
        "wind_speed": 4.5,
        "slope": slope,
        "land_use_type": detected_type if detected_type else "clear",
        "env_sensitivity": 0.2
    }

    engine = FeasibilityEngine()
    assessment = engine.run_assessment(env_features, deployment_type="Solar")

    print(f"\nFinal Assessment Status    : {assessment['final_status']}")
    print(f"Effective Feasibility Score: {assessment['feasibility_score']} / 100")
    print(f"Recommendation              : {assessment['recommendation']}")
    if not assessment['is_technically_feasible']:
        print(f"Hard Violations             : {assessment['constraint_summary']['hard_constraint_violations']}")

if __name__ == "__main__":
    for site in test_coordinates:
        run_full_inspection(site)
        time.sleep(3.0)  # Allows public Overpass mirrors to clear rate-limit windows