import os
import json
import time
import logging
import threading
from pathlib import Path
import joblib
from typing import Dict, Any, Optional, Union, List, Tuple
import pandas as pd
import numpy as np

from app.ml.serialization import ModelSerializer
from app.ml.schemas import FeatureVector
from app.feature_engineering.feature_builder import FeatureBuilder
from app.services.feasibility.feasibility_engine import TechnicalFeasibilityEngine

logger = logging.getLogger("ml.prediction")


class ProductionPredictor:
    """
    Singleton production predictor that loads serialized best_model.joblib artifact once,
    loads scaler.joblib, label_encoder.joblib, and feature_columns.json if present,
    caches them in memory, validates feature order & bounds, and computes inference results.
    Does NOT retrain models automatically if missing.
    """

    _instance = None
    _lock = threading.Lock()
    _cached_artifact: Optional[Dict[str, Any]] = None

    def __new__(cls, models_dir: Optional[str] = None):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ProductionPredictor, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, models_dir: Optional[str] = None):
        if self._initialized:
            return
        self.serializer = ModelSerializer(models_dir)
        self.feature_builder = FeatureBuilder()
        self.feasibility_engine = TechnicalFeasibilityEngine()
        self._initialized = True

    def clear_cache(self) -> None:
        """
        Clears in-memory model cache when a new model is serialized.
        """
        with self._lock:
            self._cached_artifact = None
            logger.info("In-memory prediction model cache cleared.")

    def load_model(self, force_reload: bool = False) -> Dict[str, Any]:
        """
        Loads serialized best_model.joblib artifact, scaler.joblib, label_encoder.joblib, feature_columns.json.
        Raises RuntimeError if model file is absent (NO automatic retraining).
        """
        if not force_reload and self._cached_artifact is not None:
            return self._cached_artifact

        with self._lock:
            if not force_reload and self._cached_artifact is not None:
                return self._cached_artifact

            artifact = ModelSerializer.load_best_model()

            if artifact is None:
                err_msg = (
                    "Serialized model (best_model.joblib) not found. "
                    "Please train models first by calling POST /ml/train."
                )
                logger.error("Inference Error: %s", err_msg)
                raise RuntimeError(err_msg)

            models_dir = self.serializer.models_dir

            # Load feature_columns.json if present
            feat_path = models_dir / "feature_columns.json"
            if feat_path.exists():
                try:
                    with open(feat_path, "r", encoding="utf-8") as f:
                        artifact["feature_names"] = json.load(f)
                except Exception as e:
                    logger.warning("Failed to load feature_columns.json: %s", e)

            # Load scaler.joblib if present
            scaler_path = models_dir / "scaler.joblib"
            if scaler_path.exists() and "preprocessor" in artifact and artifact["preprocessor"] is not None:
                try:
                    artifact["preprocessor"].scaler = joblib.load(scaler_path)
                except Exception as e:
                    logger.warning("Failed to load scaler.joblib: %s", e)

            # Load label_encoder.joblib if present
            le_path = models_dir / "label_encoder.joblib"
            if le_path.exists():
                try:
                    artifact["label_encoder"] = joblib.load(le_path)
                except Exception as e:
                    logger.warning("Failed to load label_encoder.joblib: %s", e)

            self._cached_artifact = artifact
            logger.info("Model Loaded: Successfully loaded '%s' into inference engine", artifact.get("model_name", "best_model"))
            return self._cached_artifact

    def is_model_loaded(self) -> bool:
        """
        Returns True if best_model.joblib exists and can be loaded.
        """
        try:
            artifact = self.load_model()
            return artifact is not None
        except Exception:
            return False

    def validate_and_format_features(
        self,
        raw_features: Union[Dict[str, Any], FeatureVector, pd.DataFrame],
        expected_features: List[str]
    ) -> Tuple[pd.DataFrame, List[str]]:
        """
        Validates feature input, applies coordinate defaults, and enforces feature column ordering.
        """
        if isinstance(raw_features, FeatureVector):
            input_dict = raw_features.dict()
        elif isinstance(raw_features, pd.DataFrame):
            input_dict = raw_features.iloc[0].to_dict() if len(raw_features) > 0 else {}
        elif isinstance(raw_features, dict):
            input_dict = dict(raw_features)
        else:
            raise ValueError(f"Unsupported feature input type: {type(raw_features)}")

        # Coordinates sanity check
        lat = input_dict.get("latitude")
        lon = input_dict.get("longitude")
        if lat is not None:
            lat = float(lat)
            if not (-90.0 <= lat <= 90.0):
                raise ValueError(f"Latitude must be between -90 and 90, got {lat}")

        if lon is not None:
            lon = float(lon)
            if not (-180.0 <= lon <= 180.0):
                raise ValueError(f"Longitude must be between -180 and 180, got {lon}")

        # Enrich via feature builder if lat/lon available
        if lat is not None and lon is not None:
            built = self.feature_builder.build_features(lat, lon)
            for k, v in built.items():
                if k not in input_dict or input_dict[k] is None:
                    input_dict[k] = v

        domain_defaults = {
            "latitude": 26.9124, "longitude": 75.7873, "solar_irradiance": 5.2,
            "wind_speed": 6.5, "temperature": 25.0, "humidity": 50.0,
            "elevation": 250.0, "slope": 2.0, "road_distance": 4.0,
            "substation_distance": 8.0, "accessibility": 80.0, "terrain_score": 75.0,
            "environmental_score": 85.0, "infrastructure_score": 80.0,
            "capacity_factor": 25.0, "season": "Summer", "month": 7,
            "day": 15, "week_number": 28, "day_of_year": 196, "quarter": 3,
            "weekend_flag": 0, "leap_year_flag": 0, "wind_class": "Good", "solar_class": "High"
        }

        missing_features = []
        validated_dict = {}

        for col in expected_features:
            if col in input_dict and input_dict[col] is not None:
                val = input_dict[col]
                if isinstance(val, (int, float, np.number)):
                    if np.isnan(val) or np.isinf(val):
                        val = domain_defaults.get(col, 0.0)
                validated_dict[col] = val
            else:
                missing_features.append(col)
                validated_dict[col] = domain_defaults.get(col, 0.0)

        df_ordered = pd.DataFrame([validated_dict], columns=expected_features)
        return df_ordered, missing_features

    def predict(
        self,
        feature_data: Union[Dict[str, Any], FeatureVector, pd.DataFrame],
        prediction_type: str = "regression"
    ) -> Dict[str, Any]:
        """
        Executes model prediction using serialized best_model.joblib without retraining.
        Calculates execution time in milliseconds.
        """
        t0 = time.perf_counter()

        logger.info("Prediction request received")
        artifact = self.load_model()
        model = artifact["model"]
        preprocessor = artifact["preprocessor"]
        label_encoder = artifact.get("label_encoder") or getattr(preprocessor, "label_encoder", None)
        expected_features = artifact.get("feature_names", [])
        feature_importance = artifact.get("feature_importance", {})
        target_variable = artifact.get("target_variable", "solar_irradiance")
        actual_pred_type = artifact.get("prediction_type", prediction_type)

        df_input, missing_cols = self.validate_and_format_features(feature_data, expected_features)
        X_scaled, _ = preprocessor.encode_and_scale(df_input, is_training=False)

        raw_pred = model.predict(X_scaled)[0]

        if actual_pred_type == "classification":
            if hasattr(model, "predict_proba"):
                probas = model.predict_proba(X_scaled)[0]
                confidence = float(np.max(probas)) * 100.0
            else:
                confidence = 85.0

            if label_encoder is not None and isinstance(raw_pred, (int, np.integer)):
                pred_value = str(label_encoder.inverse_transform([int(raw_pred)])[0])
            else:
                pred_value = str(raw_pred)
        else:
            r2 = artifact.get("metrics", {}).get("r2", artifact.get("metrics", {}).get("r2_score", 0.85))
            confidence = float(min(99.0, max(70.0, r2 * 100.0)))
            pred_value = float(round(raw_pred, 4))

        t1 = time.perf_counter()
        processing_time_ms = round((t1 - t0) * 1000.0, 2)

        top_items = list(feature_importance.items())[:3]
        if top_items:
            top_str = ", ".join([f"{k} ({v*100:.1f}%)" if v <= 1.0 else f"{k} ({v:.2f})" for k, v in top_items])
            explanation_str = f"Prediction for '{target_variable}' = {pred_value} is driven primarily by key features: {top_str}."
        else:
            explanation_str = f"Prediction for '{target_variable}' = {pred_value} based on standard physical feature inputs."

        logger.info("Prediction completed: Predicted '%s' = %s in %.2fms", target_variable, str(pred_value), processing_time_ms)

        # ── Technical Feasibility Validation Engine ─────────────────────────────
        raw_feat_dict = df_input.iloc[0].to_dict() if not df_input.empty else {}
        if isinstance(feature_data, FeatureVector):
            raw_feat_dict.update(feature_data.dict())
        elif isinstance(feature_data, dict):
            raw_feat_dict.update(feature_data)

        feasibility_res = self.feasibility_engine.evaluate_feasibility(
            features=raw_feat_dict,
            ml_prediction=str(pred_value)
        )

        return {
            "target_variable": target_variable,
            "prediction_type": actual_pred_type,
            "selected_model": artifact.get("model_name", "Best Model"),
            "prediction": pred_value,
            "confidence_score": round(confidence, 1),
            "explanation": explanation_str,
            "processing_time": processing_time_ms,
            "processing_time_ms": processing_time_ms,
            "feature_importance": feature_importance,
            "missing_features_imputed": missing_cols,
            "prediction_status": "Success",
            "technical_feasibility": feasibility_res.technical_feasibility,
            "feasibility_score": feasibility_res.feasibility_score,
            "feasibility_rating": feasibility_res.feasibility_rating,
            "engineering_decision": feasibility_res.engineering_decision,
            "engineering_recommendation": feasibility_res.engineering_recommendation,
            "hard_constraints": feasibility_res.hard_constraints.dict(),
            "soft_constraints": feasibility_res.soft_constraints,
            "constraint_summary": feasibility_res.constraint_summary,
        }


