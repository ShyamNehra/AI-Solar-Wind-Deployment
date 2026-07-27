import pytest
from pydantic import ValidationError
from app.services.analysis_pipeline import AnalysisPipeline, SiteAnalysisRequest
from app.services.energy_estimator import DeploymentType

pipeline = AnalysisPipeline()

def test_pipeline_valid_execution():
    """Verify end-to-end execution across all modules."""
    payload = SiteAnalysisRequest(
        site_id="SITE_RAJASTHAN_001",
        latitude=26.9124,
        longitude=75.7873,
        available_land_area_sqm=120000.0,
        slope=4.5,
        env_sensitivity=0.15,
        distance_to_grid=2.5,
        solar_irradiance=5.8,
        wind_speed=6.2,
        solar_capacity_mw=15.0,
        wind_capacity_mw=10.0,
        technology=DeploymentType.HYBRID
    )
    
    response = pipeline.run(payload)
    
    # Validation checks
    assert response.site_id == "SITE_RAJASTHAN_001"
    assert "latitude" in response.coordinates
    assert response.solar_assessment["suitability"] == "High"
    assert response.site_evaluation.overall_score > 0
    assert response.energy_yield.total_annual_mwh > 0
    assert response.deployment_recommendation.expansion_feasible is True

def test_pipeline_invalid_inputs():
    """Ensure invalid parameters trigger schema validation errors gracefully."""
    with pytest.raises(ValidationError):
        # Invalid latitude out of bounds (> 90)
        SiteAnalysisRequest(
            site_id="INVALID_SITE",
            latitude=120.0,
            longitude=75.0,
            available_land_area_sqm=1000.0,
            slope=-5.0,  # Invalid negative slope
            env_sensitivity=1.5,  # Out of range (> 1.0)
            distance_to_grid=-1.0
        )