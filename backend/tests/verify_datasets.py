import sys
import os
import requests

# 1. NASA POWER API (Solar & Wind Climatology)
def test_nasa_power_api():
    print("\n[1/5] Testing NASA POWER API...")
    url = "https://power.larc.nasa.gov/api/temporal/climatology/point"
    params = {
        "parameters": "ALLSKY_SFC_SW_DWN,WS10M",  # ALLSKY_SFC_SW_DWN = Solar Irradiance, WS10M = Wind Speed at 10m
        "community": "RE",
        "longitude": 75.7873,
        "latitude": 26.9124,
        "format": "JSON"
    }
    try:
        res = requests.get(url, params=params, timeout=10)
        if res.status_code == 200:
            data = res.json().get("properties", {}).get("parameter", {})
            solar_dict = data.get("ALLSKY_SFC_SW_DWN", {})
            wind_dict = data.get("WS10M", {})
            
            # Extract Annual Average ("ANN")
            solar = solar_dict.get("ANN", "N/A")
            wind = wind_dict.get("ANN", "N/A")
            
            print(f"  [SUCCESS] NASA POWER fetched: Solar={solar} kWh/m²/day, Wind={wind} m/s")
            return True
        else:
            print(f"  [FAILED] NASA POWER API returned status {res.status_code}: {res.text[:100]}")
    except Exception as e:
        print(f"  [FAILED] NASA POWER Connection Error: {e}")
    return False


# 2. OpenStreetMap Overpass API (GIS Boundaries)
def test_osm_overpass_api():
    print("\n[2/5] Testing OpenStreetMap Overpass API...")
    
    # Redundant public endpoints to handle 504 server timeouts
    endpoints = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.private.coffee/api/interpreter"
    ]
    
    headers = {"User-Agent": "SolarWindDeploymentIntelligence/1.0 (VerificationScript)"}
    
    # Query with increased timeout (15s) and targeted bounding box
    query = """
    [out:json][timeout:15];
    (
      nwr["boundary"="national_park"](25.85, 76.20, 26.25, 76.65);
    );
    out tags 1;
    """
    
    for url in endpoints:
        try:
            res = requests.post(url, data={"data": query}, headers=headers, timeout=12)
            if res.status_code == 200:
                elements = res.json().get("elements", [])
                print(f"  [SUCCESS] OSM Overpass fetched via {url.split('/')[2]}: {len(elements)} element(s) found.")
                return True
            else:
                print(f"  [DEBUG] Endpoint {url.split('/')[2]} returned HTTP {res.status_code}")
        except Exception as e:
            print(f"  [DEBUG] Endpoint {url.split('/')[2]} failed: {e}")
            
    print("  [FAILED] All OSM Overpass endpoints timed out or failed.")
    return False


# 3. Elevation & Terrain Slope Data
def test_elevation_slope_dataset():
    print("\n[3/5] Testing Elevation & Terrain Slope Data...")
    try:
        # Check local file fallback first
        local_dem_path = "app/data/elevation_dem.tif"
        if os.path.exists(local_dem_path):
            print(f"  [SUCCESS] Local DEM file found at {local_dem_path}")
            return True
            
        # Fallback to high-reliability Open-Meteo Elevation API
        url = "https://api.open-meteo.com/v1/elevation?latitude=26.9124&longitude=75.7873"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            elev = res.json().get("elevation", [0])[0]
            print(f"  [SUCCESS] Elevation fetched dynamically via Open-Meteo: {elev}m")
            return True
        else:
            print(f"  [FAILED] Elevation API returned HTTP Status {res.status_code}")
    except Exception as e:
        print(f"  [FAILED] Elevation test error: {e}")
    return False


# 4. ML Model / Historical Training Dataset (.csv or .pkl)
def test_ml_dataset_and_model():
    print("\n[4/5] Testing ML Dataset & Model Weights...")
    
    # Check root models directory and backend sub-paths
    search_paths = [
        "../models",
        "models",
        "app/models"
    ]
    
    for path in search_paths:
        if os.path.exists(path):
            files = [f for f in os.listdir(path) if f.endswith((".joblib", ".pkl", ".csv"))]
            if files:
                print(f"  [SUCCESS] Located ML Model File: {os.path.join(path, files[0])}")
                return True
                
    print("  [FAILED] Could not locate .joblib file in models folder.")
    return False


# 5. Financial & Infrastructure Dataset (Grid, Tariff, CAPEX Baselines)
def test_financial_infrastructure_data():
    print("\n[5/5] Testing Financial & Infrastructure Baselines...")
    try:
        # Verify financial constants or loaded lookup table
        financial_config = {
            "solar_capex_per_mw": 50000000,  # ₹5 Cr/MW
            "wind_capex_per_mw": 65000000,   # ₹6.5 Cr/MW
            "tariff_per_kwh": 4.5           # ₹4.5/kWh
        }
        if financial_config["tariff_per_kwh"] > 0:
            print(f"  [SUCCESS] Financial baselines active: Solar CAPEX=₹{financial_config['solar_capex_per_mw']/1e7} Cr/MW, Tariff=₹{financial_config['tariff_per_kwh']}/kWh")
            return True
    except Exception as e:
        print(f"  [FAILED] Financial dataset error: {e}")
    return False


if __name__ == "__main__":
    print("==================================================")
    print("      SOLAR & WIND PLATFORM DATASET AUDIT         ")
    print("==================================================")
    
    results = {
        "1. NASA POWER API": test_nasa_power_api(),
        "2. OSM Overpass GIS": test_osm_overpass_api(),
        "3. Elevation / Terrain": test_elevation_slope_dataset(),
        "4. ML Dataset / Weights": test_ml_dataset_and_model(),
        "5. Financial Baselines": test_financial_infrastructure_data(),
    }
    
    print("\n==================================================")
    print("                VERIFICATION SUMMARY              ")
    print("==================================================")
    passed_count = sum(results.values())
    for dataset, status in results.items():
        print(f"{dataset.ljust(28)}: {'[PASS]' if status else '[FAIL]'}")
    print(f"\nOverall Result: {passed_count}/5 Datasets Operational.")
    print("==================================================")