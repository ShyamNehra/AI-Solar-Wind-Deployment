"""
Integration Tests for Unified Deployment Intelligence Pipeline

Covers:
- Five Geographical Locations Execution
- Invalid Input Validation
- Hard Constraint Rejection (ML positive, hard constraint failed)
- Soft Constraint Differential Scoring
- Energy Yield Sensitivity Scenarios
- Financial Metrics Sensitivity Scenarios
- API Response Schema Consistency
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.workflow_pipeline_service import WorkflowPipelineService

client = TestClient(app)
pipeline_service = WorkflowPipelineService()

FIVE_TEST_LOCATIONS = [
    {"name": "Thar Desert, Rajasthan", "latitude": 26.9124, "longitude": 75.7873},
    {"name": "Muppandal Wind Farm, Tamil Nadu", "latitude": 8.2259, "longitude": 77.5469},
    {"name": "Western Ghats Region", "latitude": 10.0889, "longitude": 77.0595},
    {"name": "Himalayan Foothills", "latitude": 30.3165, "longitude": 78.0322},
    {"name": "Central Indian Plain", "latitude": 23.2599, "longitude": 77.4126},
]


def test_five_location_pipeline_execution():
    """
    TASK 10 & 11: Execute pipeline across 5 different locations and verify standardized response structure.
    """
    for loc in FIVE_TEST_LOCATIONS:
        lat = loc["latitude"]
        lon = loc["longitude"]
        res = pipeline_service.run_pipeline(latitude=lat, longitude=lon)

        # Verification of complete standardized response schema
        assert "site_suitability" in res, f"Missing site_suitability for {loc['name']}"
        assert "recommended_deployment" in res, f"Missing recommended_deployment for {loc['name']}"
        assert "prediction" in res, f"Missing prediction for {loc['name']}"
        assert "prediction_explanation" in res, f"Missing prediction_explanation for {loc['name']}"
        assert "feature_importance" in res, f"Missing feature_importance for {loc['name']}"
        assert "technical_feasibility" in res, f"Missing technical_feasibility for {loc['name']}"
        assert "feasibility_score" in res, f"Missing feasibility_score for {loc['name']}"
        assert "constraint_summary" in res, f"Missing constraint_summary for {loc['name']}"
        assert "energy_yield" in res, f"Missing energy_yield for {loc['name']}"
        assert "financial_metrics" in res, f"Missing financial_metrics for {loc['name']}"
        assert "recommendation_reason" in res, f"Missing recommendation_reason for {loc['name']}"
        assert res["status"] in ["Success", "success"], f"Failed status for {loc['name']}"

        # Check constraint_summary structure
        cs = res["constraint_summary"]
        assert "hard_constraints_passed" in cs
        assert "hard_constraint_violations" in cs
        assert "soft_constraint_score" in cs

        # Check energy_yield structure
        ey = res["energy_yield"]
        assert "solar_annual_energy" in ey
        assert "wind_annual_energy" in ey
        assert "hybrid_annual_energy" in ey
        assert "selected_annual_energy_yield" in ey
        assert ey["selected_annual_energy_yield"] > 0

        # Check financial_metrics structure
        fm = res["financial_metrics"]
        assert "annual_revenue" in fm
        assert "estimated_project_cost" in fm
        assert "payback_period" in fm
        assert "roi" in fm
        assert fm["annual_revenue"] > 0
        assert fm["estimated_project_cost"] > 0


def test_invalid_inputs_pipeline():
    """
    TEST INVALID INPUTS: Verify clear error responses for bad inputs.
    """
    # 1. Invalid Latitude (> 90)
    with pytest.raises(ValueError, match="Latitude must be between -90 and 90"):
        pipeline_service.run_pipeline(latitude=105.0, longitude=75.0)

    # 2. Invalid Longitude (< -180)
    with pytest.raises(ValueError, match="Longitude must be between -180 and 180"):
        pipeline_service.run_pipeline(latitude=20.0, longitude=-210.0)

    # 3. None inputs
    with pytest.raises(ValueError):
        pipeline_service.run_pipeline(latitude=None, longitude=75.0)


def test_hard_constraint_violation_rejection():
    """
    TEST HARD CONSTRAINT SCENARIOS:
    Verify that a site with good ML/resource potential but a hard constraint failure
    (e.g., steep slope > 35° or protected forest) returns technical_feasibility = False
    and is NOT recommended for deployment.
    """
    lat, lon = 26.9124, 75.7873
    # Inject slope > 35 degrees hard constraint violation
    res = pipeline_service.run_pipeline(
        latitude=lat,
        longitude=lon,
        constraints={"slope": 42.0, "protected_forest": True}
    )

    assert res["technical_feasibility"] is False
    assert res["constraint_summary"]["hard_constraints_passed"] is False
    assert len(res["constraint_summary"]["hard_constraint_violations"]) >= 1
    assert "Protected Forest Area" in res["constraint_summary"]["hard_constraint_violations"] or "Slope > 35° (42.0°)" in res["constraint_summary"]["hard_constraint_violations"]
    assert "Not" in res["recommended_deployment"]
    assert res["site_suitability"] == "Not Suitable"


def test_soft_constraint_differential_scoring():
    """
    TEST SOFT CONSTRAINT SCENARIOS:
    Compare Site A (excellent infrastructure) vs Site B (moderate infrastructure).
    Both pass hard constraints, but receive different feasibility scores.
    """
    lat, lon = 26.9124, 75.7873

    # Site A: Good infrastructure (close to road & grid)
    res_a = pipeline_service.run_pipeline(
        latitude=lat,
        longitude=lon,
        constraints={"road_distance": 2.0, "substation_distance": 3.0, "accessibility": 95.0}
    )

    # Site B: Moderate infrastructure (further from road & grid)
    res_b = pipeline_service.run_pipeline(
        latitude=lat,
        longitude=lon,
        constraints={"road_distance": 10.0, "substation_distance": 12.0, "accessibility": 60.0}
    )

    assert res_a["technical_feasibility"] is True
    assert res_b["technical_feasibility"] is True
    assert res_a["feasibility_score"] > res_b["feasibility_score"]
    assert res_a["constraint_summary"]["soft_constraint_score"] > res_b["constraint_summary"]["soft_constraint_score"]


def test_energy_yield_scenarios():
    """
    TEST ENERGY SCENARIOS:
    Verify resource, capacity factor, system efficiency, and loss sensitivities.
    """
    from app.services.energy.solar_energy import estimate_solar_energy
    from app.services.energy.wind_energy import estimate_wind_energy

    # 1. Higher solar irradiance -> higher solar energy yield
    solar_low = estimate_solar_energy(solar_irradiance=3.5, installed_capacity=1000)
    solar_high = estimate_solar_energy(solar_irradiance=6.5, installed_capacity=1000)
    assert solar_high > solar_low

    # 2. Higher wind speed -> higher wind energy yield
    wind_low = estimate_wind_energy(wind_speed=4.0, installed_capacity=1000)
    wind_high = estimate_wind_energy(wind_speed=9.0, installed_capacity=1000)
    assert wind_high > wind_low

    # 3. Higher operational losses -> lower energy yield
    solar_loss_10 = estimate_solar_energy(solar_irradiance=5.5, installed_capacity=1000, operational_loss=0.10)
    solar_loss_25 = estimate_solar_energy(solar_irradiance=5.5, installed_capacity=1000, operational_loss=0.25)
    assert solar_loss_10 > solar_loss_25


def test_financial_scenarios():
    """
    TEST FINANCIAL SCENARIOS:
    Verify revenue, tariff, project cost, payback period, and ROI calculations.
    """
    from app.services.financial.financial_service import FinancialAnalysisService
    fin_svc = FinancialAnalysisService()

    # 1. Higher energy yield -> higher revenue
    fin_low_yield = fin_svc.analyze_financials(annual_energy_yield=1000000.0, electricity_tariff=90.0)
    fin_high_yield = fin_svc.analyze_financials(annual_energy_yield=2000000.0, electricity_tariff=90.0)
    assert fin_high_yield["annual_revenue"] > fin_low_yield["annual_revenue"]

    # 2. Higher tariff -> higher revenue
    fin_low_tariff = fin_svc.analyze_financials(annual_energy_yield=1000000.0, electricity_tariff=50.0)
    fin_high_tariff = fin_svc.analyze_financials(annual_energy_yield=1000000.0, electricity_tariff=100.0)
    assert fin_high_tariff["annual_revenue"] > fin_low_tariff["annual_revenue"]

    # 3. Higher project cost -> longer payback
    fin_low_cost = fin_svc.analyze_financials(annual_energy_yield=1000000.0, cost_per_mw=20000000.0)
    fin_high_cost = fin_svc.analyze_financials(annual_energy_yield=1000000.0, cost_per_mw=60000000.0)
    assert fin_high_cost["payback_period"] > fin_low_cost["payback_period"]

    # 4. Higher revenue -> higher ROI
    assert fin_high_yield["roi"] > fin_low_yield["roi"]
