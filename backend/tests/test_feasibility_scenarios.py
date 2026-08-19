# tests/test_feasibility_scenarios.py
from app.evaluation.feasibility_engine import FeasibilityEngine

def test_scenario_1_hard_constraint_rejection():
    """Verify that sites violating hard constraints are rejected regardless of high potential energy."""
    engine = FeasibilityEngine()
    
    # High irradiance & wind, but on steep slope in a protected wetland zone
    invalid_site = {
        "solar_irradiance": 7.5,
        "wind_speed": 12.0,
        "slope": 22.0,                   # Hard violation (> 15°)
        "land_use_type": "wetland",      # Hard violation (restricted)
        "distance_to_grid_km": 1.0,
        "distance_to_road_km": 0.5
    }

    result = engine.run_assessment(invalid_site, deployment_type="solar")
    
    assert result["is_technically_feasible"] is False
    assert result["final_status"] == "REJECTED"
    assert result["feasibility_score"] == 0.0
    assert len(result["constraint_summary"]["hard_constraint_violations"]) == 2
    print("\n[OK] Scenario 1 Passed: Hard constraint violation triggered REJECTED status.")


def test_scenario_2_soft_constraint_variations():
    """Verify valid sites receive varying feasibility scores based on infrastructure proximity."""
    engine = FeasibilityEngine()

    # Prime site near grid & roads
    prime_site = {
        "solar_irradiance": 6.0,
        "slope": 3.0,
        "land_use_type": "unrestricted",
        "distance_to_grid_km": 2.0,      # Close
        "distance_to_road_km": 1.0       # Close
    }

    # Remote site far from grid
    remote_site = {
        "solar_irradiance": 6.0,
        "slope": 3.0,
        "land_use_type": "unrestricted",
        "distance_to_grid_km": 25.0,     # Far
        "distance_to_road_km": 12.0      # Far
    }

    prime_res = engine.run_assessment(prime_site, "solar")
    remote_res = engine.run_assessment(remote_site, "solar")

    assert prime_res["is_technically_feasible"] is True
    assert remote_res["is_technically_feasible"] is True
    assert prime_res["feasibility_score"] > remote_res["feasibility_score"]
    assert prime_res["final_status"] == "APPROVED"
    assert remote_res["final_status"] == "CONDITIONAL"
    print(f"\n[OK] Scenario 2 Passed: Prime site scored {prime_res['feasibility_score']}, Remote site scored {remote_res['feasibility_score']}.")

def test_ocean_region_rejection():
    """Verify that offshore marine/ocean coordinates are automatically detected as water bodies and rejected."""
    engine = FeasibilityEngine()

    ocean_sites = [
        {"name": "Southern Ocean (South of Kanyakumari)", "latitude": 7.4060, "longitude": 77.1832, "solar_irradiance": 5.16, "wind_speed": 3.6, "slope": 2.8},
        {"name": "Arabian Sea (Offshore Kerala)", "latitude": 8.3202, "longitude": 75.9007, "solar_irradiance": 5.15, "wind_speed": 3.58, "slope": 2.2}
    ]

    for site in ocean_sites:
        res = engine.run_assessment(site, deployment_type="solar")
        assert res["is_technically_feasible"] is False, f"Failed: Ocean site {site['name']} was not marked as unfeasible!"
        assert res["final_status"] == "REJECTED", f"Failed: Ocean site {site['name']} status was not REJECTED!"
        assert res["feasibility_score"] == 0.0, f"Failed: Ocean site {site['name']} score was not 0.0!"
        assert res["land_type"] == "water_body", f"Failed: Ocean site {site['name']} land_type was not water_body!"
        print(f"\n[OK] Ocean Check Passed: {site['name']} properly REJECTED as {res['land_type']}.")


if __name__ == "__main__":
    test_scenario_1_hard_constraint_rejection()
    test_scenario_2_soft_constraint_variations()
    test_ocean_region_rejection()