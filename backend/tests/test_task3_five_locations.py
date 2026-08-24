"""
Task 3 - Automated Integration Tests for Solar & Wind Deployment Intelligence Platform

Tests 5 Distinct Geographical & Constraint Locations:
1. High Solar Location -> Expected: Solar Farm (Recommended for Solar Deployment)
2. High Wind Location -> Expected: Wind Farm (Recommended for Wind Deployment)
3. High Solar + High Wind Location -> Expected: Hybrid (Recommended for Hybrid Deployment)
4. Restricted Area / High Slope -> Expected: Not Technically Feasible (technical_feasibility = False)
5. Poor Resource Location -> Expected: Low Suitability / Not Recommended

Verifies:
- Successful execution
- Correct deployment recommendation
- Technical feasibility status & scores
- Energy yield estimations
- Financial calculations (Revenue, Project Cost, Payback, ROI)
- Consistent API responses matching UnifiedDeploymentResponse schema
- Invalid input handling
- No pipeline failures
"""

import pytest
from app.services.workflow_pipeline_service import WorkflowPipelineService
from app.schemas.unified_response import UnifiedDeploymentResponse

pipeline_service = WorkflowPipelineService()


def test_location_1_high_solar():
    """
    Location 1: High Solar (Thar Desert, Rajasthan)
    Expected: Solar Farm / Recommended for Solar Deployment
    """
    # High solar irradiance (6.5), low wind speed (3.5)
    res = pipeline_service.run_pipeline(
        latitude=26.9124,
        longitude=75.7873,
        constraints={"solar_irradiance": 6.5, "wind_speed": 3.5}
    )

    # Validate response schema
    validated = UnifiedDeploymentResponse(**res)
    assert validated.status == "Success"
    assert validated.technical_feasibility is True
    assert "Solar" in validated.recommended_deployment
    assert validated.annual_energy_yield > 0
    assert validated.annual_revenue > 0
    assert validated.estimated_project_cost > 0
    assert validated.payback_period > 0
    assert validated.roi > 0


def test_location_2_high_wind():
    """
    Location 2: High Wind (Muppandal Wind Farm, Tamil Nadu)
    Expected: Wind Farm / Recommended for Wind Deployment
    """
    # Moderate solar (4.2), high wind speed (8.5)
    res = pipeline_service.run_pipeline(
        latitude=8.2259,
        longitude=77.5469,
        constraints={"solar_irradiance": 4.2, "wind_speed": 8.5}
    )

    validated = UnifiedDeploymentResponse(**res)
    assert validated.status == "Success"
    assert validated.technical_feasibility is True
    assert "Wind" in validated.recommended_deployment
    assert validated.annual_energy_yield > 0
    assert validated.annual_revenue > 0
    assert validated.roi > 0


def test_location_3_high_solar_and_high_wind():
    """
    Location 3: High Solar + High Wind (Coastal Kutch, Gujarat)
    Expected: Hybrid / Recommended for Hybrid Deployment
    """
    # High solar (6.2), high wind speed (7.8)
    res = pipeline_service.run_pipeline(
        latitude=23.2198,
        longitude=69.6669,
        constraints={"solar_irradiance": 6.2, "wind_speed": 7.8}
    )

    validated = UnifiedDeploymentResponse(**res)
    assert validated.status == "Success"
    assert validated.technical_feasibility is True
    assert "Hybrid" in validated.recommended_deployment
    assert validated.annual_energy_yield > 0
    assert validated.annual_revenue > 0


def test_location_4_restricted_area():
    """
    Location 4: Restricted Area / Steep Slope / Protected Forest
    Expected: Not Technically Feasible
    """
    res = pipeline_service.run_pipeline(
        latitude=30.3165,
        longitude=78.0322,
        constraints={"slope": 45.0, "protected_forest": True}
    )

    validated = UnifiedDeploymentResponse(**res)
    assert validated.status == "Success"
    assert validated.technical_feasibility is False
    assert validated.recommended_deployment == "Technically Not Feasible"
    assert validated.site_suitability == "Not Suitable"
    assert "not feasible" in validated.recommendation_reason.lower() or "violation" in validated.recommendation_reason.lower()


def test_location_5_poor_resources():
    """
    Location 5: Poor Resources (Low Solar & Low Wind)
    Expected: Low Suitability / Not Recommended
    """
    res = pipeline_service.run_pipeline(
        latitude=20.0,
        longitude=90.0,
        constraints={"solar_irradiance": 2.1, "wind_speed": 2.0}
    )

    validated = UnifiedDeploymentResponse(**res)
    assert validated.status == "Success"
    assert ("Not Recommended" in validated.recommended_deployment or 
            "Technically Not Feasible" in validated.recommended_deployment or
            "Low" in validated.site_suitability or 
            "Poor" in validated.site_suitability or 
            "Not Suitable" in validated.site_suitability)


def test_pipeline_invalid_input_handling():
    """
    Verify invalid coordinates raise ValueError for proper API HTTP status mapping.
    """
    with pytest.raises(ValueError):
        pipeline_service.run_pipeline(latitude=150.0, longitude=75.0)

    with pytest.raises(ValueError):
        pipeline_service.run_pipeline(latitude=20.0, longitude=-200.0)

    with pytest.raises(ValueError):
        pipeline_service.run_pipeline(latitude=None, longitude=75.0)
