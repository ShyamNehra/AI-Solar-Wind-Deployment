"""
Model Serialization Module.
Handles persisting trained model artifacts, preprocessors, and metadata.json under backend/models/.
"""

import os
import json
import logging
from pathlib import Path
import joblib
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List

logger = logging.getLogger("ml.serialization")


class ModelSerializer:
    """
    Serializes selected best model artifact, scaler, encoders, feature columns,
    and metadata to backend/models/.
    """

    def __init__(self, models_dir: Optional[str] = None):
        if models_dir is None:
            base_dir = Path(__file__).resolve().parent.parent.parent
            self.models_dir = base_dir / "models"
        else:
            self.models_dir = Path(models_dir)

        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.best_model_path = self.models_dir / "best_model.joblib"
        self.metadata_path = self.models_dir / "model_metadata.json"
        self.best_model_metadata_path = self.models_dir / "best_model_metadata.json"
        self.feature_columns_path = self.models_dir / "feature_columns.json"
        self.scaler_path = self.models_dir / "scaler.joblib"
        self.label_encoder_path = self.models_dir / "label_encoder.joblib"
        self.comparison_csv_path = self.models_dir / "comparison_results.csv"

        # Legacy fallback paths for backward compatibility with earlier tests
        self.regressor_path = self.models_dir / "random_forest_regressor.joblib"
        self.classifier_path = self.models_dir / "random_forest_classifier.joblib"

    def serialize_best_model(
        self,
        winner_candidate: Dict[str, Any],
        winner_row: Dict[str, Any],
        preprocessor: Any,
        target_variable: str,
        prediction_type: str,
        feature_names: List[str],
        sample_count: int,
        reason: str,
        ranking_score: float = 0.0,
        comparison_table: Optional[List[Dict[str, Any]]] = None,
        label_encoder: Any = None
    ) -> Tuple[str, str]:
        """
        Saves best_model.joblib, scaler.joblib, label_encoder.joblib, feature_columns.json,
        model_metadata.json, best_model_metadata.json, and comparison_results.csv.
        Returns Tuple of (joblib_path_str, metadata_path_str).
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        model = winner_candidate["model"]
        algo_key = winner_candidate.get("algorithm", "random_forest")
        display_name = winner_row.get("model", algo_key)
        metrics = winner_row.get("metrics", {})

        payload = {
            "model": model,
            "preprocessor": preprocessor,
            "prediction_type": prediction_type,
            "algorithm": algo_key,
            "model_name": display_name,
            "target_variable": target_variable,
            "feature_names": feature_names,
            "feature_importance": winner_row.get("feature_importance", {}),
            "metrics": metrics,
            "training_time": winner_row.get("training_time", 0.0),
            "prediction_time": winner_row.get("prediction_time", 0.0),
            "model_size": winner_row.get("model_size", "0 KB"),
            "sample_count": sample_count,
            "trained_on": timestamp,
            "selection_reason": reason,
            "ranking_score": ranking_score
        }

        # 1. Save best_model.joblib
        joblib.dump(payload, self.best_model_path)

        # Also save legacy paths for backward compatibility if code checks prediction_type specifically
        if prediction_type == "classification":
            joblib.dump(payload, self.classifier_path)
        else:
            joblib.dump(payload, self.regressor_path)

        # 2. Save feature_columns.json
        with open(self.feature_columns_path, "w", encoding="utf-8") as f:
            json.dump(feature_names, f, indent=2)

        # 3. Save scaler.joblib
        if hasattr(preprocessor, "scaler") and preprocessor.scaler is not None:
            joblib.dump(preprocessor.scaler, self.scaler_path)

        # 4. Save label_encoder.joblib (if classification or label_encoder present)
        le_to_save = label_encoder or getattr(preprocessor, "label_encoder", None)
        if le_to_save is not None:
            joblib.dump(le_to_save, self.label_encoder_path)

        # 5. Save best_model_metadata.json
        best_metadata = {
            "best_model_name": display_name,
            "algorithm": algo_key,
            "prediction_type": prediction_type,
            "target_variable": target_variable,
            "reason": reason,
            "evaluation_metrics": metrics,
            "ranking_score": ranking_score,
            "trained_on": timestamp,
            "sample_count": sample_count,
            "feature_count": len(feature_names),
            "training_time": winner_row.get("training_time", 0.0),
            "prediction_time": winner_row.get("prediction_time", 0.0)
        }
        with open(self.best_model_metadata_path, "w", encoding="utf-8") as f:
            json.dump(best_metadata, f, indent=2)

        # 6. Save model_metadata.json
        metadata = {
            "model": display_name,
            "selected_model": display_name,
            "algorithm": algo_key,
            "prediction_type": prediction_type,
            "target_variable": target_variable,
            "mae": metrics.get("mae", 0.0),
            "rmse": metrics.get("rmse", 0.0),
            "r2": metrics.get("r2", metrics.get("r2_score", 0.0)),
            "accuracy": metrics.get("accuracy", 0.0),
            "f1_score": metrics.get("f1_score", 0.0),
            "trained_on": timestamp,
            "reason": reason,
            "ranking_score": ranking_score,
            "sample_count": sample_count,
            "feature_names": feature_names,
            "metrics": metrics,
            "training_time": winner_row.get("training_time", 0.0),
            "prediction_time": winner_row.get("prediction_time", 0.0),
            "model_size": winner_row.get("model_size", "0 KB"),
            "comparison_table": comparison_table or []
        }
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        # 7. Save comparison_results.csv if comparison_table is provided
        if comparison_table:
            try:
                comp_df = pd.DataFrame(comparison_table)
                # Drop nested objects like metrics or feature_importance if needed for clean CSV
                clean_cols = [c for c in comp_df.columns if c not in ["metrics", "feature_importance", "confusion_matrix"]]
                comp_df[clean_cols].to_csv(self.comparison_csv_path, index=False)
            except Exception as e:
                logger.warning("Failed to save comparison_results.csv: %s", e)

        logger.info(
            "Model Serialized Successfully: Saved best model to '%s', feature columns to '%s', and metadata to '%s'",
            self.best_model_path, self.feature_columns_path, self.best_model_metadata_path
        )

        # Invalidate in-memory cache in inference engine so new model is picked up on next predict call
        try:
            from app.ml.inference import ModelInferenceModule
            ModelInferenceModule().clear_cache()
        except Exception:
            pass

        return str(self.best_model_path), str(self.best_model_metadata_path)

    @staticmethod
    def load_best_model() -> Optional[Dict[str, Any]]:
        """
        Loads serialized best_model.joblib artifact from disk.
        Returns None if not present.
        """
        models_dir = Path(__file__).resolve().parent.parent.parent / "models"
        best_path = models_dir / "best_model.joblib"

        if not best_path.exists():
            # Try regressor or classifier as fallback
            reg_path = models_dir / "random_forest_regressor.joblib"
            cls_path = models_dir / "random_forest_classifier.joblib"
            if reg_path.exists():
                best_path = reg_path
            elif cls_path.exists():
                best_path = cls_path
            else:
                return None

        try:
            artifact = joblib.load(best_path)
            return artifact
        except Exception as e:
            logger.error("Error loading model from '%s': %s", best_path, str(e))
            return None

    @staticmethod
    def load_metadata() -> Optional[Dict[str, Any]]:
        """
        Loads model_metadata.json or best_model_metadata.json from disk.
        Returns None if not present.
        """
        models_dir = Path(__file__).resolve().parent.parent.parent / "models"
        meta_path = models_dir / "model_metadata.json"
        if not meta_path.exists():
            meta_path = models_dir / "best_model_metadata.json"

        if not meta_path.exists():
            return None

        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error("Error reading metadata from '%s': %s", meta_path, str(e))
            return None

