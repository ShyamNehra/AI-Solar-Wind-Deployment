"""
Unit and Integration Tests for Model Inference Module, Caching, Feature Validation Pipeline,
Backend Services Integration, and FastAPI Endpoints.
"""

import pytest
import numpy as np
import pandas as pd
from fastapi.testclient import TestClient

from app.main import app
from app.ml.inference import ModelInferenceModule
from app.ml.model_loader import ModelPersistence
from app.ml.schemas import FeatureVector
from app.services.deployment_strategy import recommend_strategy
from app.services.assessment_service import AssessmentService
from app.services.workflow_pipeline_service import WorkflowPipelineService

client = TestClient(app)


@pytest.fixture
def auth_headers():
    username = "inference_test_user_unique_1"
    password = "password123"
    client.post("/auth/register", json={"username": username, "password": password, "role": "Renewable Energy Planner"})
    resp = client.post(
        "/auth/login",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = resp.json().get("access_token", "")
    return {"Authorization": f"Bearer {token}"}


def test_inference_module_singleton_and_caching():
    """
    Task 1 & Task 2: Verifies ModelInferenceModule singleton instance and single-load caching via joblib.
    """
    module1 = ModelInferenceModule()
    module2 = ModelInferenceModule()
    assert module1 is module2

    # Load model cached
    artifact1 = module1.load_model_cached("regression")
    assert artifact1 is not None

    artifact2 = module1.load_model_cached("regression")
    assert artifact1 is artifact2  # Memory reference equality proves single load / reuse

    # Verify cache clearing
    module1.clear_cache("regression")
    assert "regression" not in module1._model_cache


def test_feature_validation_completeness_and_ordering():
    """
    Task 3: Verifies feature validation, completeness handling, and exact column ordering.
    """
    module = ModelInferenceModule()
    artifact = module.load_model_cached("regression")
    expected_features = artifact["feature_names"]

    # Input with missing optional fields and arbitrary column order
    partial_input = {
        "wind_speed": 7.2,
        "latitude": 26.9,
        "longitude": 75.7
    }

    df_validated, missing_cols = module.validate_and_format_features(partial_input, expected_features)

    # 1. Enforces exact feature ordering
    assert list(df_validated.columns) == expected_features

    # 2. Populates missing columns gracefully
    assert len(df_validated) == 1
    assert df_validated["wind_speed"].iloc[0] == 7.2
    assert df_validated["latitude"].iloc[0] == 26.9


def test_invalid_feature_handling():
    """
    Task 3 & Task 5: Verifies invalid/out-of-bound inputs raise descriptive ValueError.
    """
    module = ModelInferenceModule()

    # Invalid latitude out of bounds
    invalid_lat = {"latitude": 150.0, "longitude": 75.0}

    with pytest.raises(ValueError) as exc_info:
        module.validate_and_format_features(invalid_lat, ["latitude", "longitude"])
    assert "Latitude must be between -90 and 90" in str(exc_info.value)


def test_prediction_pipeline_execution():
    """
    Task 3: Verifies complete prediction pipeline output structure.
    """
    module = ModelInferenceModule()
    sample_features = {
        "latitude": 26.9124,
        "longitude": 75.7873,
        "solar_irradiance": 6.1,
        "wind_speed": 7.5,
        "temperature": 28.0,
        "humidity": 45.0,
        "elevation": 300.0,
        "slope": 2.0,
        "road_distance": 3.0,
        "substation_distance": 6.0
    }

    res = module.predict(sample_features, prediction_type="regression")

    assert res["prediction_status"] == "Success"
    assert "prediction" in res
    assert isinstance(res["prediction"], (float, int))
    assert 0.0 <= res["confidence_score"] <= 100.0
    assert "feature_importance" in res


def test_backend_strategy_recommendation_integration():
    """
    Task 4: Verifies recommend_strategy incorporates ML model prediction.
    """
    res = recommend_strategy(
        solar_suitability="Excellent",
        wind_suitability="Excellent",
        solar_irradiance=6.8,
        wind_speed=8.2,
        latitude=26.9124,
        longitude=75.7873
    )

    assert "deployment" in res
    assert res["deployment"] in ["Solar", "Wind", "Hybrid", "Not Recommended"]
    assert "confidence" in res
    assert "reason" in res
    assert "ml_prediction" in res


def test_assessment_and_pipeline_services_integration():
    """
    Task 4 & Task 5: Verifies AssessmentService and WorkflowPipelineService with ML predictions.
    """
    assessment_service = AssessmentService()
    report = assessment_service.perform_assessment(26.9124, 75.7873)

    assert "deployment_recommendation" in report
    rec = report["deployment_recommendation"]
    assert rec["deployment"] in ["Solar", "Wind", "Hybrid", "Not Recommended"]
    assert rec["confidence"] > 0

    pipeline_service = WorkflowPipelineService()
    pipe_res = pipeline_service.run_pipeline(26.9124, 75.7873)
    assert "assessment_result" in pipe_res
    assert "deployment_optimization" in pipe_res


def test_fastapi_ml_predict_and_error_endpoints(auth_headers):
    """
    Task 5: End-to-end testing of FastAPI /ml/predict endpoint and error handling.
    """
    # 1. Valid prediction request
    resp = client.post(
        "/ml/predict",
        json={"latitude": 26.9124, "longitude": 75.7873, "model_type": "regression"},
        headers=auth_headers
    )
    assert resp.status_code == 200
    json_data = resp.json()
    assert json_data["prediction_status"] == "Success"

    # 2. Invalid feature vector with out-of-range latitude
    invalid_resp = client.post(
        "/ml/predict",
        json={"feature_vector": {"latitude": 195.0, "longitude": 75.7873}},
        headers=auth_headers
    )
    assert invalid_resp.status_code == 422  # Pydantic validation error or HTTP 400
