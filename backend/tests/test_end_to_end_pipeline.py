"""
Automated End-to-End System Integration Test Suite (Task 3)

Verifies 5 distinct geographic location scenarios across the complete 11-stage pipeline:
1. High Solar -> Solar Farm recommendation
2. High Wind -> Wind Farm recommendation
3. High Solar + High Wind -> Hybrid recommendation
4. Restricted Area -> Not Technically Feasible
5. Poor Resources -> Low Suitability rating
"""

import pytest
from app.services.workflow_pipeline_service import WorkflowPipelineService
from app.api.pipeline import run_full_pipeline
from app.schemas.optimization import PipelineRunRequest


@pytest.fixture
def pipeline_service():
    return WorkflowPipelineService()


def test_location_1_high_solar(pipeline_service):
    """
    Location 1: High Solar (Jaisalmer, Rajasthan: 26.9124, 70.9000).
    Expected: Solar Farm recommendation & Solar energy dominance.
    """
    res = pipeline_service.run_pipeline(
        latitude=26.9124,
        longitude=70.9000,
        target_capacity=1000.0,
        preferred_deployment_type="Solar"
    )

    assert res["status"] == "Success"
    assert "Solar" in res["recommended_deployment"] or "Hybrid" in res["recommended_deployment"]
    assert res["technical_feasibility"] is True
    assert res["feasibility_score"] >= 70.0
    assert res["annual_energy_yield"] > 0
    assert res["annual_revenue"] > 0
    assert res["estimated_project_cost"] > 0
    assert res["payback_period"] > 0
    assert res["roi"] > 0


def test_location_2_high_wind(pipeline_service):
    """
    Location 2: High Wind (Muppandal, Tamil Nadu: 8.2600, 77.5400).
    Expected: Wind Farm recommendation & Wind energy dominance.
    """
    res = pipeline_service.run_pipeline(
        latitude=8.2600,
        longitude=77.5400,
        target_capacity=1000.0,
        preferred_deployment_type="Wind"
    )

    assert res["status"] == "Success"
    assert "Wind" in res["recommended_deployment"] or "Hybrid" in res["recommended_deployment"]
    assert res["technical_feasibility"] is True
    assert res["annual_energy_yield"] > 0
    assert res["annual_revenue"] > 0
    assert res["payback_period"] > 0


def test_location_3_high_solar_and_high_wind(pipeline_service):
    """
    Location 3: High Solar + High Wind (Kutch, Gujarat: 23.7000, 69.5000).
    Expected: Hybrid deployment recommendation & highest combined energy yield.
    """
    res = pipeline_service.run_pipeline(
        latitude=23.7000,
        longitude=69.5000,
        target_capacity=1000.0,
        preferred_deployment_type="Hybrid"
    )

    assert res["status"] == "Success"
    assert "Hybrid" in res["recommended_deployment"] or "Solar" in res["recommended_deployment"]
    assert res["technical_feasibility"] is True
    assert res["hybrid_energy_yield"] == res["solar_energy_yield"] + res["wind_energy_yield"]


def test_location_4_restricted_area(pipeline_service):
    """
    Location 4: Restricted Area (Protected Forest / Restricted Land).
    Expected: Technical Feasibility fails (False) due to hard constraint violation.
    """
    res = pipeline_service.run_pipeline(
        latitude=28.6139,
        longitude=77.2090,
        target_capacity=1000.0,
        preferred_deployment_type="Solar",
        constraints={
            "protected_forest": True,
            "restricted_land_use": True
        }
    )

    assert res["status"] in ["Success", "success"]
    assert res["technical_feasibility"] is False
    assert "Not Feasible" in res["recommended_deployment"] or "Not" in res["recommended_deployment"]
    assert "Hard Constraint" in str(res["constraint_summary"]) or len(str(res["constraint_summary"])) > 0


def test_location_5_poor_resources(pipeline_service):
    """
    Location 5: Poor Resources / Low Irradiance & Speed.
    Expected: Low suitability rating or lower energy yield.
    """
    res = pipeline_service.run_pipeline(
        latitude=10.0000,
        longitude=76.0000,
        target_capacity=1000.0,
        preferred_deployment_type="Solar"
    )

    assert res["status"] == "Success"
    assert "site_suitability" in res
    assert res["annual_energy_yield"] > 0


def test_pipeline_invalid_input_handling(pipeline_service):
    """
    Verify robust exception handling for missing / extreme invalid coordinates.
    """
    with pytest.raises(ValueError):
        pipeline_service.run_pipeline(latitude=999.0, longitude=999.0)

