import sys
import os
import requests

# Add root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.analysis_pipeline import AnalysisPipelineService
from schemas.analysis import AnalysisRequest

# 5 Regional Locations across India
LOCATIONS = [
    {
        "name": "Jaisalmer, Rajasthan (Solar Dominant)",
        "latitude": 26.9124,
        "longitude": 70.9083,
        "elevation": 220.0,
        "slope": 0.5,
    },
    {
        "name": "Muppandal, Tamil Nadu (Wind Dominant)",
        "latitude": 8.2588,
        "longitude": 77.5369,
        "elevation": 80.0,
        "slope": 1.2,
    },
    {
        "name": "Puri, Odisha (Hybrid Coastline)",
        "latitude": 19.8135,
        "longitude": 85.8312,
        "elevation": 15.0,
        "slope": 0.8,
    },
    {
        "name": "Khavda, Gujarat (High Solar & Wind)",
        "latitude": 23.8732,
        "longitude": 69.8594,
        "elevation": 45.0,
        "slope": 1.0,
    },
    {
        "name": "Leh, Ladakh (High Solar Altitude)",
        "latitude": 34.1526,
        "longitude": 77.5771,
        "elevation": 3500.0,
        "slope": 2.5,
    }
]

# Required response keys for JSON consistency verification
REQUIRED_KEYS = [
    "project",
    "solar_features",
    "wind_features",
    "site_evaluation",
    "site_score",
    "deployment_recommendation",
    "predicted_overall_score",
    "predicted_deployment",
    "top_features",
    "explanation",
    "technical_feasibility",
    "technical_feasibility_score",
    "constraint_violations",
    "critical_violations",
    "overall_status",
    "solar_energy_yield_kwh",
    "wind_energy_yield_kwh",
    "hybrid_energy_yield_kwh",
    "recommended_annual_energy_kwh",
    "annual_revenue",
    "estimated_project_cost",
    "payback_period",
    "roi"
]

def run_e2e_tests():
    print("=== Running End-to-End Integration Tests ===")
    
    # Check if local uvicorn endpoint is accessible
    use_http = True
    base_url = "http://127.0.0.1:8000/analysis"
    try:
        # Simple health check check
        requests.get("http://127.0.0.1:8000/health", timeout=2)
        print("FastAPI local server is active. Running tests via HTTP requests.")
    except requests.exceptions.RequestException:
        print("FastAPI local server is not accessible. Running tests via local Service class fallback.")
        use_http = False

    pipeline_service = None if use_http else AnalysisPipelineService()

    # 1. Test 5 valid locations
    for idx, loc in enumerate(LOCATIONS, start=1):
        print(f"\nLocation {idx}: {loc['name']}")
        
        payload = {
            "project_name": f"E2E Test Project {idx}",
            "location": loc["name"],
            "latitude": loc["latitude"],
            "longitude": loc["longitude"],
            "elevation": loc["elevation"],
            "slope": loc["slope"],
            "distance_to_road": 1.5,
            "distance_to_grid": 5.0,
            "installed_capacity_kw": 1200.0,
            "electricity_tariff_inr_per_kwh": 8.5,
            "cost_per_kw": 22000.0,
            "additional_installation_percentage": 12.0
        }

        if use_http:
            response = requests.post(base_url, json=payload)
            assert response.status_code == 200, f"HTTP request failed with status {response.status_code}"
            data = response.json()
        else:
            # Service class direct validation
            request_obj = AnalysisRequest(**payload)
            data = pipeline_service.run_analysis(request_obj)

        # Verify all output fields exist (JSON structure consistency)
        for key in REQUIRED_KEYS:
            assert key in data, f"Missing required response key: '{key}' in response of {loc['name']}"

        print(f"[OK] Validated {loc['name']} successfully.")
        print(f"     Deployment Recommendation: {data['deployment_recommendation']['deployment']}")
        print(f"     Annual Yield: {data['recommended_annual_energy_kwh']} kWh | Revenue: {data['annual_revenue']} INR")
        print(f"     Project Cost: {data['estimated_project_cost']} INR | Payback: {data['payback_period']} Years")

    # 2. Test invalid coordinate bounds
    print("\n=== Testing Invalid Coordinates and Inputs ===")
    invalid_payloads = [
        # Latitude too high
        {"latitude": 95.0, "longitude": 75.0, "project_name": "Invalid", "location": "Test"},
        # Latitude too low
        {"latitude": -95.0, "longitude": 75.0, "project_name": "Invalid", "location": "Test"},
        # Longitude too high
        {"latitude": 20.0, "longitude": 185.0, "project_name": "Invalid", "location": "Test"},
        # Longitude too low
        {"latitude": 20.0, "longitude": -185.0, "project_name": "Invalid", "location": "Test"}
    ]

    for idx, invalid in enumerate(invalid_payloads):
        payload = {
            "project_name": invalid["project_name"],
            "location": invalid["location"],
            "latitude": invalid["latitude"],
            "longitude": invalid["longitude"]
        }

        if use_http:
            response = requests.post(base_url, json=payload)
            # Validation errors should return HTTP 422 or controlled exception responses
            print(f"Invalid input payload {idx+1} status code (expected error): {response.status_code}")
            assert response.status_code != 200
        else:
            try:
                request_obj = AnalysisRequest(**payload)
                pipeline_service.run_analysis(request_obj)
                assert False, f"Expected ValueError for invalid coordinates {payload}"
            except ValueError as e:
                print(f"Invalid input payload {idx+1} raised expected error: {e}")

    # 3. Test non-numeric coordinates inputs
    payload_bad_type = {
        "project_name": "Bad Type",
        "location": "Test",
        "latitude": "NotANumber",
        "longitude": 75.0
    }
    if use_http:
        response = requests.post(base_url, json=payload_bad_type)
        print(f"Bad type payload status code (expected error): {response.status_code}")
        assert response.status_code == 422  # FastAPI Pydantic type validation failure
    else:
        try:
            # Pydantic validation checks types upon initialization
            AnalysisRequest(**payload_bad_type)
            assert False, "Pydantic did not raise ValidationError for non-numeric type coordinate"
        except Exception as e:
            print(f"Bad type payload raised expected type validation error: {type(e).__name__}")

    print("\nAll end-to-end integration and consistency checks passed successfully!")

if __name__ == "__main__":
    run_e2e_tests()
