# tests/test_multi_location_pipeline.py
import pytest
from app.schemas.site import StandardizedSiteAssessmentRequest
from app.services.analysis_pipeline import AnalysisPipeline


def test_five_geographic_locations():
    """Tests pipeline across 5 diverse site locations."""
    pipeline = AnalysisPipeline()

    test_sites = [
        {"site_id": "SITE_RAJASTHAN_SOLAR", "lat": 26.9124, "lon": 75.7873, "slope": 2.0},   # Jaipur, Solar rich
        {"site_id": "SITE_TAMILNADU_WIND", "lat": 8.0883, "lon": 77.5385, "slope": 4.0},    # Kanyakumari, Wind rich
        {"site_id": "SITE_GUJARAT_HYBRID", "lat": 23.2156, "lon": 72.6369, "slope": 3.5},    # Gandhinagar, Hybrid
        {"site_id": "SITE_LADAKH_HIGH_ALT", "lat": 34.1526, "lon": 77.5771, "slope": 5.0},   # Leh, High Irradiance
        {"site_id": "SITE_MAHARASHTRA_HILL", "lat": 18.5204, "lon": 73.8567, "slope": 18.0}  # Pune, High Slope (Steep)
    ]

    for site in test_sites:
        req = StandardizedSiteAssessmentRequest(
            site_id=site["site_id"],
            latitude=site["lat"],
            longitude=site["lon"],
            slope=site["slope"]
        )

        res = pipeline.run_full_analysis(req)

        # Assertions
        assert res.site_id == site["site_id"]
        assert res.status == "SUCCESS"
        assert res.financial_metrics["estimated_project_cost_inr"] > 0
        assert res.energy_yield["annual_net_yield_mwh"] >= 0

        # Special check: High slope site should fail feasibility
        if site["slope"] > 15.0:
            assert res.technical_feasibility["is_technically_feasible"] is False
            assert res.technical_feasibility["final_status"] == "REJECTED"


def test_invalid_input_handling():
    """Verifies input boundary validation using Pydantic."""
    with pytest.raises(ValueError):
        # Invalid Latitude > 90
        StandardizedSiteAssessmentRequest(site_id="INVALID_LAT", latitude=105.0, longitude=75.0)

    with pytest.raises(ValueError):
        # Invalid Negative Land Area
        StandardizedSiteAssessmentRequest(site_id="INVALID_AREA", latitude=20.0, longitude=75.0, available_land_area_sqm=-500.0)