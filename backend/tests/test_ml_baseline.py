"""
Unit and Integration Tests for Machine Learning Baseline Models, Evaluation Metrics,
Multi-Algorithm Comparison, Model Behavior Diagnostics, and FastAPI Endpoint Integration.
"""

import pytest
import numpy as np
import pandas as pd
from fastapi.testclient import TestClient
from pathlib import Path

from app.main import app
from app.ml.evaluator import MLEvaluator
from app.ml.trainer import MLTrainer
from app.ml.data_loader import MLDataLoader
from app.ml.model_loader import ModelPersistence
from app.ml.predictor import MLPredictor
from app.auth.auth_handler import create_access_token

client = TestClient(app)

@pytest.fixture
def auth_headers():
    username = "ml_test_user_unique_1"
    password = "password123"
    client.post("/auth/register", json={"username": username, "password": password, "role": "Renewable Energy Planner"})
    resp = client.post(
        "/auth/login",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = resp.json().get("access_token", "")
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def sample_dataset():
    loader = MLDataLoader()
    return loader.generate_training_dataset(num_samples=200)


def test_mlevaluator_regression_metrics():
    """
    Tests calculation of MAE, MSE, RMSE, R², and MAPE metrics.
    """
    evaluator = MLEvaluator()
    y_true = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
    y_pred = np.array([11.0, 19.0, 31.0, 38.0, 52.0])

    metrics = evaluator.evaluate_regression(y_true, y_pred)

    assert "mae" in metrics
    assert "mse" in metrics
    assert "rmse" in metrics
    assert "r2_score" in metrics
    assert "mape" in metrics

    assert metrics["mae"] > 0
    assert metrics["mse"] > 0
    assert metrics["rmse"] == round(np.sqrt(metrics["mse"]), 4)
    assert metrics["r2_score"] > 0.90
    assert metrics["mape"] > 0.0


def test_mltrainer_dataset_split(sample_dataset):
    """
    Tests 70/15/15 train-validation-test dataset split.
    """
    trainer = MLTrainer()
    X_df, y_series, _ = trainer.feature_selector.split_features_and_target(sample_dataset, "solar_irradiance")
    X_scaled, _ = trainer.preprocessor.encode_and_scale(X_df, is_training=True)

    X_train, X_val, X_test, y_train, y_val, y_test = trainer.split_dataset(
        X_scaled, y_series, train_ratio=0.70, val_ratio=0.15, test_ratio=0.15, random_state=42
    )

    total_samples = len(sample_dataset)
    assert len(X_train) == int(total_samples * 0.70)
    assert len(X_val) + len(X_test) == total_samples - len(X_train)
    assert len(y_train) == len(X_train)
    assert len(y_val) == len(X_val)
    assert len(y_test) == len(X_test)


def test_linear_regression_baseline_training(sample_dataset):
    """
    Tests baseline training of Linear Regression model.
    """
    trainer = MLTrainer()
    res = trainer.train_baseline(
        df=sample_dataset,
        target_variable="solar_irradiance",
        algorithm="linear_regression",
        random_state=42
    )

    assert res["algorithm"] == "linear_regression"
    assert res["prediction_type"] == "regression"
    assert "mae" in res["metrics"]
    assert "r2_score" in res["metrics"]
    assert "model_behavior" in res
    assert res["model"] is not None


def test_decision_tree_and_random_forest_baselines(sample_dataset):
    """
    Tests baseline training of Decision Tree and Random Forest algorithms.
    """
    trainer = MLTrainer()

    dt_res = trainer.train_baseline(sample_dataset, target_variable="solar_irradiance", algorithm="decision_tree")
    rf_res = trainer.train_baseline(sample_dataset, target_variable="solar_irradiance", algorithm="random_forest")

    assert dt_res["algorithm"] == "decision_tree"
    assert rf_res["algorithm"] == "random_forest"
    assert dt_res["metrics"]["r2_score"] is not None
    assert rf_res["metrics"]["r2_score"] is not None


def test_multi_model_comparison_and_diagnostics(sample_dataset):
    """
    Tests comparing Linear Regression, Decision Tree, and Random Forest baselines.
    Verifies comparative metrics table, behavior diagnostics (underfit/overfit/generalizing well), and winner selection.
    """
    trainer = MLTrainer()
    comp = trainer.compare_baselines(
        df=sample_dataset,
        target_variable="solar_irradiance",
        algorithms=["linear_regression", "decision_tree", "random_forest"]
    )

    assert "comparison_table" in comp
    assert len(comp["comparison_table"]) == 3
    assert comp["best_algorithm"] in ["linear_regression", "decision_tree", "random_forest"]
    assert comp["best_score"] > -1.0
    assert "split_info" in comp

    for row in comp["comparison_table"]:
        assert "algorithm" in row
        assert "validation_metrics" in row
        assert "train_metrics" in row
        assert "test_metrics" in row
        assert "behavior_analysis" in row


def test_joblib_model_persistence(sample_dataset):
    """
    Tests saving and loading trained models using joblib.
    """
    trainer = MLTrainer()
    persistence = ModelPersistence()

    trained_res = trainer.train_baseline(sample_dataset, target_variable="solar_irradiance", algorithm="linear_regression")
    saved_path = persistence.save_model(trained_res, prediction_type="regression")

    assert Path(saved_path).exists()

    loaded_artifact = persistence.load_model("regression")
    assert loaded_artifact is not None
    assert loaded_artifact["prediction_type"] == "regression"
    assert "model" in loaded_artifact
    assert "preprocessor" in loaded_artifact


def test_fastapi_ml_endpoints(auth_headers):
    """
    Tests FastAPI /ml/train, /ml/compare, /ml/status, /ml/metrics, and /ml/predict endpoints.
    """
    # 1. Train endpoint
    train_res = client.post(
        "/ml/train",
        json={"target_variable": "solar_irradiance", "algorithm": "linear_regression", "random_state": 42},
        headers=auth_headers
    )
    assert train_res.status_code == 200
    assert train_res.json()["status"] == "Success"
    assert train_res.json()["algorithm"] == "linear_regression"

    # 2. Compare endpoint
    compare_res = client.post(
        "/ml/compare",
        json={"target_variable": "solar_irradiance", "algorithms": ["linear_regression", "decision_tree", "random_forest"]},
        headers=auth_headers
    )
    assert compare_res.status_code == 200
    comp_json = compare_res.json()
    assert comp_json["status"] == "Success"
    assert len(comp_json["comparison_table"]) == 3
    assert comp_json["best_algorithm"] in ["linear_regression", "decision_tree", "random_forest"]

    # 3. Status endpoint
    status_res = client.get("/ml/status", headers=auth_headers)
    assert status_res.status_code == 200
    assert status_res.json()["regressor_exists"] is True

    # 4. Metrics endpoint
    metrics_res = client.get("/ml/metrics", headers=auth_headers)
    assert metrics_res.status_code == 200
    assert metrics_res.json()["overall_status"] == "Ready"

    # 5. Predict endpoint
    predict_res = client.post(
        "/ml/predict",
        json={"latitude": 26.9124, "longitude": 75.7873, "model_type": "regression"},
        headers=auth_headers
    )
    assert predict_res.status_code == 200
    pred_json = predict_res.json()
    assert pred_json["prediction_status"] == "Success"
    assert isinstance(pred_json["prediction"], (str, float))
