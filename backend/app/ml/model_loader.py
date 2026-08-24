"""
Model Persistence and Loader Utility using Joblib.
Stores models under backend/models/ (best_model.joblib, metadata.json).
"""

import os
from pathlib import Path
import joblib
from datetime import datetime
from typing import Dict, Any, Tuple, Optional

from app.ml.serialization import ModelSerializer

class ModelPersistence:
    """
    Utility wrapper for model persistence supporting best_model.joblib and metadata.json.
    """

    def __init__(self, models_dir: Optional[str] = None):
        self.serializer = ModelSerializer(models_dir)
        self.models_dir = self.serializer.models_dir
        self.best_model_path = self.serializer.best_model_path
        self.metadata_path = self.serializer.metadata_path
        self.regressor_path = self.serializer.regressor_path
        self.classifier_path = self.serializer.classifier_path

    def get_model_path(self, prediction_type: str = "regression") -> Path:
        if self.best_model_path.exists():
            return self.best_model_path
        if prediction_type == "classification":
            return self.classifier_path
        return self.regressor_path

    def save_model(
        self,
        model_artifact: Dict[str, Any],
        prediction_type: str = "regression"
    ) -> str:
        """
        Persists trained model artifact to best_model.joblib and metadata files.
        """
        winner_candidate = {
            "model": model_artifact["model"],
            "algorithm": model_artifact.get("algorithm", "random_forest")
        }
        winner_row = {
            "model": f"{model_artifact.get('algorithm', 'random_forest').replace('_', ' ').title()}",
            "metrics": model_artifact.get("metrics", {}),
            "feature_importance": model_artifact.get("feature_importance", {}),
            "training_time": model_artifact.get("training_time", 0.0),
            "prediction_time": model_artifact.get("prediction_time", 0.0),
            "model_size": model_artifact.get("model_size", "0 KB")
        }
        reason = model_artifact.get("model_behavior", "Optimal baseline model selected for deployment.")
        ranking_score = model_artifact.get("ranking_score", 0.0)
        comparison_table = model_artifact.get("comparison_table")
        label_encoder = model_artifact.get("label_encoder")

        best_joblib, meta_json = self.serializer.serialize_best_model(
            winner_candidate=winner_candidate,
            winner_row=winner_row,
            preprocessor=model_artifact["preprocessor"],
            target_variable=model_artifact.get("target_variable", "solar_irradiance"),
            prediction_type=prediction_type,
            feature_names=model_artifact.get("feature_names", []),
            sample_count=model_artifact.get("sample_count", 0),
            reason=reason,
            ranking_score=ranking_score,
            comparison_table=comparison_table,
            label_encoder=label_encoder
        )
        return best_joblib

    def load_model(
        self, prediction_type: str = "regression"
    ) -> Optional[Dict[str, Any]]:
        """
        Loads saved model artifact from disk if present.
        """
        return ModelSerializer.load_best_model()

    def load_metadata(self) -> Optional[Dict[str, Any]]:
        return ModelSerializer.load_metadata()

    def model_exists(self, prediction_type: str = "regression") -> bool:
        """
        Returns True if best_model.joblib or specific prediction_type joblib exists.
        """
        if self.best_model_path.exists():
            return True
        return self.get_model_path(prediction_type).exists()

