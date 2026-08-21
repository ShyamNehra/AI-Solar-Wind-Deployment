import sys
import os

# Add root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.feasibility_engine import TechnicalFeasibilityEngine
from app.services.analysis_pipeline import AnalysisPipelineService
from schemas.analysis import AnalysisRequest

# Mock Clients to prevent network connection errors during testing
class MockNASAPowerClient:
    def get_solar_data(self, latitude: float, longitude: float) -> dict:
        return {
            "properties": {
                "parameter": {
                    "ALLSKY_SFC_SW_DWN": {"ANN": 5.4},
                    "T2M": {"ANN": 28.5},
                    "RH2M": {"ANN": 62.0}
                }
            }
        }

class MockGlobalWindAtlasClient:
    def get_wind_data(self, latitude: float, longitude: float) -> dict:
        raise NotImplementedError("Use WindFeatureEngineer fallback mock data")

def test_feasibility_engine_scenarios():
    print("=== Testing Technical Feasibility Engine ===")
    engine = TechnicalFeasibilityEngine()

    # 1. Valid site profile
    valid_site = {
        "slope": 5.0,
        "protected_area_distance": 10.0,
        "elevation": 200.0,
        "environmental_impact_level": 2.0,
        "distance_to_grid": 5.0,
        "distance_to_road": 1.0,
        "land_cost_per_acre": 8000.0,
        "grid_connection_cost": 30000.0
    }
    res_valid = engine.evaluate_site(valid_site)
    print(f"Valid Site Result: Feasible={res_valid['technical_feasibility']}, Score={res_valid['technical_feasibility_score']}, Status={res_valid['overall_status']}")
    assert res_valid["technical_feasibility"] is True
    assert res_valid["technical_feasibility_score"] > 70
    assert res_valid["overall_status"] == "Feasible"
    assert res_valid["constraint_violations"] == 0

    # 2. Hard constraint violation (slope > 20)
    steep_site = {
        "slope": 22.5,
        "protected_area_distance": 10.0,
        "elevation": 200.0,
        "environmental_impact_level": 2.0
    }
    res_steep = engine.evaluate_site(steep_site)
    print(f"Steep Site Result: Feasible={res_steep['technical_feasibility']}, Violations={res_steep['constraint_violations']}, Critical={res_steep['critical_violations']}, Status={res_steep['overall_status']}")
    assert res_steep["technical_feasibility"] is False
    assert res_steep["constraint_violations"] == 1
    assert "Slope Limit Exceeded" in res_steep["critical_violations"][0]
    assert res_steep["overall_status"] == "Unfeasible"

    # 3. Hard constraint violation (protected area < 2km)
    protected_site = {
        "slope": 5.0,
        "protected_area_distance": 1.5,
        "elevation": 200.0,
        "environmental_impact_level": 2.0
    }
    res_prot = engine.evaluate_site(protected_site)
    print(f"Protected Proximity Site Result: Feasible={res_prot['technical_feasibility']}, Violations={res_prot['constraint_violations']}, Critical={res_prot['critical_violations']}, Status={res_prot['overall_status']}")
    assert res_prot["technical_feasibility"] is False
    assert res_prot["constraint_violations"] == 1
    assert "Protected Area Proximity" in res_prot["critical_violations"][0]

    # 4. Multiple soft constraints changing feasibility scores
    remote_site = {
        "slope": 5.0,
        "protected_area_distance": 10.0,
        "elevation": 200.0,
        "environmental_impact_level": 2.0,
        "distance_to_grid": 45.0,  # far from grid (low score)
        "distance_to_road": 18.0,  # far from road (low score)
        "land_cost_per_acre": 40000.0,  # expensive land
        "grid_connection_cost": 180000.0  # high connection cost
    }
    res_remote = engine.evaluate_site(remote_site)
    print(f"Remote Site (Poor Soft constraints) Score: {res_remote['technical_feasibility_score']}")
    assert res_remote["technical_feasibility"] is True  # still feasible as they are soft constraints
    assert res_remote["technical_feasibility_score"] < res_valid["technical_feasibility_score"]

    print("[OK] Feasibility engine tests passed!\n")

def test_pipeline_integration():
    print("=== Testing Analysis Pipeline Integration ===")
    
    # Construct pipeline with mocked clients
    pipeline = AnalysisPipelineService(
        nasa_client=MockNASAPowerClient(),
        wind_client=MockGlobalWindAtlasClient()
    )

    # Create a valid request
    request = AnalysisRequest(
        project_name="Odisha Coastal Wind & Solar",
        location="Puri District",
        latitude=19.8135,
        longitude=85.8312,
        elevation=15.0,
        slope=1.2,
        distance_to_road=0.5,
        distance_to_grid=3.5,
        protected_area_distance=8.0,
        environmental_impact_level=1.5,
        land_cost_per_acre=12000.0,
        grid_connection_cost=45000.0
    )

    # Run analysis
    res = pipeline.run_analysis(request)
    
    print("Consolidated Analysis Response Keys:")
    for k in res.keys():
        print(f"  - {k}")

    # Assert new explainability/feasibility keys are populated
    assert "predicted_overall_score" in res
    assert "predicted_deployment" in res
    assert "explanation" in res
    assert "technical_feasibility" in res
    assert "technical_feasibility_score" in res
    assert "overall_status" in res
    
    print(f"ML predicted suitability: {res['predicted_overall_score']}")
    print(f"Feasibility status: {res['overall_status']} (Score={res['technical_feasibility_score']})")
    assert res["technical_feasibility"] is True
    assert res["overall_status"] == "Feasible"

    # Test invalid coordinate input validation
    print("\nTesting Invalid Coordinates handling in Pipeline:")
    invalid_req = AnalysisRequest(
        project_name="Invalid Project",
        location="Out of bounds",
        latitude=150.0,  # Invalid
        longitude=85.8312
    )
    try:
        pipeline.run_analysis(invalid_req)
        assert False, "Should have failed with ValueError for out-of-bound latitude"
    except ValueError as ve:
        print(f"  Caught expected error: {ve}")

    print("[OK] Pipeline integration tests passed!\n")

if __name__ == "__main__":
    test_feasibility_engine_scenarios()
    test_pipeline_integration()
    print("All feasibility validation and pipeline integration tests completed successfully!")
