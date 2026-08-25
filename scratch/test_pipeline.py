import sys
import os

# Add root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from schemas.analysis import AnalysisRequest
from app.services.analysis_pipeline import AnalysisPipelineService
from app.api.analysis import run_site_analysis

def test_pipeline_unit():
    print("=== Running Pipeline Unit Tests ===")
    service = AnalysisPipelineService()
    
    # 1. Test Valid Coordinates (Odisha, India)
    req_valid = AnalysisRequest(
        project_name="Odisha Hybrid Plant",
        location="Odisha Coast",
        latitude=19.8135,
        longitude=85.8312,
        elevation=25.0,
        slope=1.5,
        distance_to_road=2.0,
        distance_to_grid=5.0,
        protected_area_distance=15.0,
        environmental_impact_level=1.0,
        land_cost_per_acre=8000.0,
        grid_connection_cost=40000.0
    )
    
    print("Executing run_analysis with valid request...")
    res = service.run_analysis(req_valid)
    
    # Assertions
    assert res["project"]["project_name"] == "Odisha Hybrid Plant"
    assert res["project"]["location"] == "Odisha Coast"
    assert "solar_irradiance" in res["solar_features"]
    assert "temperature" in res["solar_features"]
    assert "humidity" in res["solar_features"]
    assert "wind_speed" in res["wind_features"]
    assert "overall_score" in res["site_score"]
    assert "deployment" in res["deployment_recommendation"]
    
    print("Valid Response structure:")
    import json
    print(json.dumps(res, indent=2))
    print("[OK] Valid coordinates unit test passed!\n")

    # 2. Test Invalid Latitude
    print("Testing coordinate validation: Invalid Latitude...")
    try:
        req_invalid_lat = AnalysisRequest(
            project_name="Invalid Lat",
            location="Somewhere",
            latitude=95.0,
            longitude=85.8
        )
        service.run_analysis(req_invalid_lat)
        assert False, "Should have raised ValueError for invalid latitude"
    except ValueError as ve:
        print(f"[OK] Caught expected ValueError: {ve}")

    # 3. Test Invalid Longitude
    print("Testing coordinate validation: Invalid Longitude...")
    try:
        req_invalid_lon = AnalysisRequest(
            project_name="Invalid Lon",
            location="Somewhere",
            latitude=20.0,
            longitude=-190.0
        )
        service.run_analysis(req_invalid_lon)
        assert False, "Should have raised ValueError for invalid longitude"
    except ValueError as ve:
        print(f"[OK] Caught expected ValueError: {ve}")


def test_api_endpoint_directly():
    print("=== Running API Endpoint Function Tests Directly ===")
    
    payload = AnalysisRequest(
        project_name="Rajasthan Hybrid Project",
        location="Rajasthan Desert",
        latitude=26.9124,
        longitude=75.7873,
        elevation=220.0,
        slope=0.5,
        distance_to_road=1.2,
        distance_to_grid=10.0,
        protected_area_distance=25.0,
        environmental_impact_level=0.5,
        land_cost_per_acre=5000.0,
        grid_connection_cost=80000.0
    )
    
    print("Calling run_site_analysis function directly with explicit service instance...")
    res = run_site_analysis(payload, pipeline=AnalysisPipelineService())
    
    assert res["project"]["project_name"] == "Rajasthan Hybrid Project"
    assert "solar_features" in res
    assert "wind_features" in res
    assert "site_evaluation" in res
    assert "site_score" in res
    assert "deployment_recommendation" in res
    print("[OK] Endpoint handler direct function test passed!\n")


if __name__ == "__main__":
    test_pipeline_unit()
    test_api_endpoint_directly()
    print("All tests completed successfully!")
