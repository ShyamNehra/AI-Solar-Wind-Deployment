"""
Automated Scenario Tests for Technical Feasibility Validation Module.
Verifies Hard Constraints, Soft Constraint Weighted Scoring, Rejection Rules, Pipeline Integration, and Scenarios 1-5.
"""

import pytest
from app.services.feasibility.feasibility_engine import TechnicalFeasibilityEngine
from app.services.feasibility.hard_constraints import HardConstraintValidator
from app.services.feasibility.soft_constraints import SoftConstraintScorer
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.fixture
def feasibility_engine():
    return TechnicalFeasibilityEngine()


@pytest.fixture
def auth_headers():
    username = "feasibility_test_user_unique_1"
    password = "password123"
    client.post("/auth/register", json={"username": username, "password": password, "role": "Renewable Energy Planner"})
    resp = client.post(
        "/auth/login",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = resp.json().get("access_token", "")
    return {"Authorization": f"Bearer {token}"}


def test_scenario_1_excellent_site(feasibility_engine):
    """
    Scenario 1: Excellent Site
    No hard constraint, high soft score.
    Expected: Prediction accepted, Feasibility 95+.
    """
    features = {
        "latitude": 26.9124,
        "longitude": 75.7873,
        "slope": 1.2,
        "road_distance": 2.0,
        "substation_distance": 3.0,
        "accessibility": 96.0,
        "terrain_score": 95.0,
        "infrastructure_score": 96.0,
        "environmental_score": 95.0,
        "protected_forest": False,
        "restricted_land_use": False
    }

    res = feasibility_engine.evaluate_feasibility(features, ml_prediction="Hybrid")

    assert res.technical_feasibility is True
    assert res.hard_constraints.passed is True
    assert len(res.hard_constraints.violations) == 0
    assert res.feasibility_score >= 95.0
    assert res.feasibility_rating == "Excellent"
    assert res.engineering_decision == "Approved"


def test_scenario_2_protected_forest(feasibility_engine):
    """
    Scenario 2: Protected Forest
    Hard constraint violated (protected forest).
    Expected: ML prediction preserved, Engineering decision = NOT FEASIBLE.
    """
    features = {
        "latitude": 26.9124,
        "longitude": 75.7873,
        "protected_forest": True,
        "slope": 2.0,
        "road_distance": 3.0,
        "substation_distance": 4.0
    }

    res = feasibility_engine.evaluate_feasibility(features, ml_prediction="Solar")

    assert res.technical_feasibility is False
    assert res.hard_constraints.passed is False
    assert "Protected Forest Area" in res.hard_constraints.violations
    assert res.engineering_decision == "NOT FEASIBLE"
    assert "ML prediction ('Solar')" in res.engineering_recommendation


def test_scenario_3_steep_terrain(feasibility_engine):
    """
    Scenario 3: Steep Terrain
    Slope > Threshold (35°).
    Expected: Rejected.
    """
    features = {
        "latitude": 26.9124,
        "longitude": 75.7873,
        "slope": 42.5,
        "road_distance": 2.0,
        "substation_distance": 3.0
    }

    res = feasibility_engine.evaluate_feasibility(features, ml_prediction="Wind")

    assert res.technical_feasibility is False
    assert res.hard_constraints.passed is False
    assert any("Slope > 35°" in v for v in res.hard_constraints.violations)
    assert res.engineering_decision == "NOT FEASIBLE"


def test_scenario_4_good_site_poor_infrastructure(feasibility_engine):
    """
    Scenario 4: Good Site, Poor Infrastructure
    Hard constraints pass, but long road and grid distances.
    Expected: Prediction accepted, Feasibility 60–70.
    """
    features = {
        "latitude": 26.9124,
        "longitude": 75.7873,
        "slope": 3.0,
        "road_distance": 12.0,
        "substation_distance": 14.0,
        "accessibility": 62.0,
        "terrain_score": 85.0,
        "infrastructure_score": 60.0,
        "environmental_score": 85.0,
        "protected_forest": False
    }

    res = feasibility_engine.evaluate_feasibility(features, ml_prediction="Hybrid")

    assert res.technical_feasibility is True
    assert res.hard_constraints.passed is True
    assert 60.0 <= res.feasibility_score <= 74.0
    assert res.engineering_decision in ["Approved", "Feasible with Conditions"]


def test_scenario_5_excellent_infrastructure_moderate_terrain(feasibility_engine):
    """
    Scenario 5: Excellent Infrastructure, Moderate Terrain
    Hard constraints pass.
    Expected: Feasibility 80+.
    """
    features = {
        "latitude": 26.9124,
        "longitude": 75.7873,
        "slope": 12.0,
        "road_distance": 1.5,
        "substation_distance": 2.5,
        "accessibility": 92.0,
        "terrain_score": 75.0,
        "infrastructure_score": 95.0,
        "environmental_score": 88.0,
        "protected_forest": False
    }

    res = feasibility_engine.evaluate_feasibility(features, ml_prediction="Solar")

    assert res.technical_feasibility is True
    assert res.hard_constraints.passed is True
    assert res.feasibility_score >= 80.0
    assert res.engineering_decision == "Approved"


def test_fastapi_ml_predict_with_feasibility(auth_headers):
    """
    Verifies POST /ml/predict returns technical feasibility details.
    """
    resp = client.post(
        "/ml/predict",
        json={"latitude": 26.9124, "longitude": 75.7873, "model_type": "regression"},
        headers=auth_headers
    )
    assert resp.status_code == 200
    data = resp.json()

    assert "technical_feasibility" in data
    assert isinstance(data["technical_feasibility"], bool)
    assert "feasibility_score" in data
    assert "engineering_decision" in data
    assert "hard_constraints" in data
    assert "soft_constraints" in data


def test_fastapi_pipeline_status_endpoint(auth_headers):
    """
    Verifies GET /pipeline/status returns pipeline and feasibility health.
    """
    resp = client.get("/pipeline/status", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()

    assert data["status"] == "Active"
    assert data["total_stages"] == 5
    assert "latest_feasibility_status" in data
