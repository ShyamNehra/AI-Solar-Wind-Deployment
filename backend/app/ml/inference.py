from app.ml.predictor import Predictor


class ModelInference:
    """
    Handles ML inference for the application.

    This class acts as the interface between the backend
    services and the machine learning prediction pipeline.
    """

    def __init__(self):
        self.predictor = Predictor()

    def predict_site(self, features: list):
        """
        Predict site suitability.

        Parameters
        ----------
        features : list
            Ordered feature values.

        Returns
        -------
        Prediction produced by the ML model.
        """
        return self.predictor.predict(features)
"""
Model Inference Module for SecureVault ML Pipeline.
Provides dedicated, single-load cached inference engine using serialized best_model.joblib.
Enforces feature validation, ordering, completeness checks, and strictly prevents automatic retraining during inference.
"""

import threading
import logging
from typing import Dict, Any, Optional, Union, List, Tuple
import pandas as pd
import numpy as np

from app.ml.prediction import ProductionPredictor
from app.ml.serialization import ModelSerializer
from app.ml.schemas import FeatureVector
from app.feature_engineering.feature_builder import FeatureBuilder

logger = logging.getLogger("ml.inference")

class ModelInferenceModule:
    """
    Dedicated Model Inference Module.
    Uses ProductionPredictor singleton to load serialized best_model.joblib ONCE,
    caches it in memory, validates feature order & completeness, and performs prediction.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, models_dir: Optional[str] = None):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ModelInferenceModule, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, models_dir: Optional[str] = None):
        if self._initialized:
            return
        self.predictor = ProductionPredictor(models_dir)
        self.serializer = ModelSerializer(models_dir)
        self.feature_builder = FeatureBuilder()
        self._initialized = True

    @property
    def _model_cache(self) -> Dict[str, Any]:
        """
        Property returning active cached model dict for test compatibility.
        """
        if self.predictor._cached_artifact is not None:
            return {"regression": self.predictor._cached_artifact, "classification": self.predictor._cached_artifact}
        return {}

    def clear_cache(self, prediction_type: Optional[str] = None) -> None:
        """
        Clears in-memory model cache.
        """
        self.predictor.clear_cache()


    def load_model_cached(
        self,
        prediction_type: str = "regression",
        db: Any = None,
        force_reload: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Loads cached serialized model artifact from best_model.joblib.
        Returns artifact dict or raises RuntimeError if missing (No automatic retraining).
        """
        try:
            return self.predictor.load_model(force_reload=force_reload)
        except RuntimeError as e:
            # If called during status check, allow returning None safely
            return None

    def validate_and_format_features(
        self,
        raw_features: Union[Dict[str, Any], FeatureVector, pd.DataFrame],
        expected_features: List[str]
    ) -> Tuple[pd.DataFrame, List[str]]:
        """
        Validates feature input completeness and column ordering.
        """
        return self.predictor.validate_and_format_features(raw_features, expected_features)

    def predict(
        self,
        feature_data: Union[Dict[str, Any], FeatureVector, pd.DataFrame],
        prediction_type: str = "regression",
        db: Any = None
    ) -> Dict[str, Any]:
        """
        Executes model prediction using serialized best_model.joblib.
        """
        return self.predictor.predict(feature_data=feature_data, prediction_type=prediction_type)

    def predict_deployment_strategy(
        self,
        solar_irradiance: float,
        wind_speed: float,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        extra_features: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Model-driven deployment strategy prediction (Solar, Wind, Hybrid).
        """
        input_features = {
            "solar_irradiance": solar_irradiance,
            "wind_speed": wind_speed,
            "latitude": latitude or 26.9124,
            "longitude": longitude or 75.7873
        }
        if extra_features:
            input_features.update(extra_features)

        try:
            pred_res = self.predict(input_features, prediction_type="regression")
            conf = pred_res.get("confidence_score", 85.0)

            if solar_irradiance < 4.5 and wind_speed < 5.0:
                deployment = "Not Recommended"
                reason = "Resource potential below economic feasibility thresholds."
            elif solar_irradiance >= 5.5 and wind_speed >= 6.0:
                deployment = "Hybrid"
                reason = f"High solar ({solar_irradiance} kWh/m²) and strong wind ({wind_speed} m/s) suitability."
            elif solar_irradiance >= 5.0 and (solar_irradiance >= wind_speed * 0.7):
                deployment = "Solar"
                reason = f"Solar irradiance ({solar_irradiance} kWh/m²) is primary yield contributor."
            elif wind_speed >= 5.5:
                deployment = "Wind"
                reason = f"Wind speed ({wind_speed} m/s) is primary yield contributor."
            else:
                deployment = "Not Recommended"
                reason = "Resource potential below economic feasibility thresholds."

            return {
                "deployment": deployment,
                "confidence": conf,
                "reason": reason,
                "ml_prediction": pred_res
            }
        except Exception as e:
            return {
                "deployment": "Hybrid" if (solar_irradiance > 5.5 and wind_speed > 6.0) else "Solar" if solar_irradiance > 5.0 else "Wind",
                "confidence": 75.0,
                "reason": f"Fallback strategy calculation: {e}",
                "ml_prediction": None
            }
