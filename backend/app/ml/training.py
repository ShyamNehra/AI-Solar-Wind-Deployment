"""
Training Pipeline for Multiple Candidate Machine Learning Models.
Supports 80/20 Train-Test split, preprocessing, model fitting, and performance timing.
"""

import time
import logging
from typing import Dict, Any, Tuple, Optional, List, Union
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.ensemble import (
    RandomForestRegressor,
    RandomForestClassifier,
    GradientBoostingRegressor,
    GradientBoostingClassifier,
    ExtraTreesRegressor,
    ExtraTreesClassifier,
)

from app.ml.preprocessing import MLPreprocessor
from app.ml.feature_selector import FeatureSelector

logger = logging.getLogger("ml.training")

# Optional XGBoost import
try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False


class ModelTrainingPipeline:
    """
    Reusable training pipeline supporting multiple candidate model architectures for regression and classification.
    """

    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.preprocessor = MLPreprocessor()
        self.feature_selector = FeatureSelector()

    def get_supported_algorithms(self, prediction_type: str = "regression") -> List[str]:
        """
        Returns list of algorithm keys supported for the given prediction task type.
        """
        algos = ["decision_tree", "random_forest", "gradient_boosting", "extra_trees", "linear"]
        if HAS_XGBOOST:
            algos.append("xgboost")
        return algos

    def instantiate_model(
        self,
        algorithm: str,
        prediction_type: str = "regression",
        hyperparameters: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Instantiates specific algorithm estimator given prediction task type and hyperparameters.
        """
        algo_key = algorithm.lower().replace(" ", "_")
        params = hyperparameters.copy() if hyperparameters else {}

        if prediction_type == "classification":
            if algo_key in ["decision_tree", "dt", "decision_tree_classifier"]:
                default_params = {"max_depth": 8, "random_state": self.random_state}
                default_params.update(params)
                return DecisionTreeClassifier(**default_params)
            elif algo_key in ["random_forest", "rf", "random_forest_classifier"]:
                default_params = {"n_estimators": 100, "max_depth": 10, "random_state": self.random_state, "n_jobs": -1}
                default_params.update(params)
                return RandomForestClassifier(**default_params)
            elif algo_key in ["gradient_boosting", "gb", "gradient_boosting_classifier"]:
                default_params = {"n_estimators": 100, "max_depth": 5, "learning_rate": 0.1, "random_state": self.random_state}
                default_params.update(params)
                return GradientBoostingClassifier(**default_params)
            elif algo_key in ["extra_trees", "et", "extra_trees_classifier"]:
                default_params = {"n_estimators": 100, "max_depth": 10, "random_state": self.random_state, "n_jobs": -1}
                default_params.update(params)
                return ExtraTreesClassifier(**default_params)
            elif algo_key in ["linear", "linear_regression", "logistic_regression", "lr"]:
                default_params = {"max_iter": 1000, "random_state": self.random_state}
                default_params.update(params)
                return LogisticRegression(**default_params)
            elif algo_key in ["xgboost", "xgb", "xgboost_classifier"] and HAS_XGBOOST:
                default_params = {"n_estimators": 100, "max_depth": 5, "random_state": self.random_state}
                default_params.update(params)
                return xgb.XGBClassifier(**default_params)
            else:
                default_params = {"n_estimators": 100, "max_depth": 10, "random_state": self.random_state, "n_jobs": -1}
                default_params.update(params)
                return RandomForestClassifier(**default_params)
        else: # Regression
            if algo_key in ["decision_tree", "dt", "decision_tree_regressor"]:
                default_params = {"max_depth": 8, "random_state": self.random_state}
                default_params.update(params)
                return DecisionTreeRegressor(**default_params)
            elif algo_key in ["random_forest", "rf", "random_forest_regressor"]:
                default_params = {"n_estimators": 100, "max_depth": 10, "random_state": self.random_state, "n_jobs": -1}
                default_params.update(params)
                return RandomForestRegressor(**default_params)
            elif algo_key in ["gradient_boosting", "gb", "gradient_boosting_regressor"]:
                default_params = {"n_estimators": 100, "max_depth": 5, "learning_rate": 0.1, "random_state": self.random_state}
                default_params.update(params)
                return GradientBoostingRegressor(**default_params)
            elif algo_key in ["extra_trees", "et", "extra_trees_regressor"]:
                default_params = {"n_estimators": 100, "max_depth": 10, "random_state": self.random_state, "n_jobs": -1}
                default_params.update(params)
                return ExtraTreesRegressor(**default_params)
            elif algo_key in ["linear", "linear_regression", "lr"]:
                return LinearRegression(**params)
            elif algo_key in ["xgboost", "xgb", "xgboost_regressor"] and HAS_XGBOOST:
                default_params = {"n_estimators": 100, "max_depth": 5, "random_state": self.random_state}
                default_params.update(params)
                return xgb.XGBRegressor(**default_params)
            else:
                default_params = {"n_estimators": 100, "max_depth": 10, "random_state": self.random_state, "n_jobs": -1}
                default_params.update(params)
                return RandomForestRegressor(**default_params)

    def train_candidates(
        self,
        df: pd.DataFrame,
        target_variable: str = "solar_irradiance",
        model_type: str = "auto",
        algorithms: Optional[List[str]] = None,
        test_size: float = 0.2,
        hyperparameters: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Trains candidate models on reproducible train-test split (random_state=42),
        records fit time, inference latency, model parameters, and feature importances.
        """
        logger.info("Training Started: Preparing dataset with %d samples for target '%s'", len(df), target_variable)

        if df.empty:
            raise ValueError("Training dataset cannot be empty.")

        X_df, y_series, detected_type = self.feature_selector.split_features_and_target(df, target_variable)
        actual_type = detected_type if model_type == "auto" else model_type

        # Handle label encoding if target is categorical / classification
        label_encoder = None
        if actual_type == "classification":
            if y_series.dtype == object or y_series.dtype.name == "category" or str(y_series.dtype) == "string":
                label_encoder = LabelEncoder()
                y_series = pd.Series(label_encoder.fit_transform(y_series.astype(str)), index=y_series.index)
                self.preprocessor.label_encoder = label_encoder

        # Preprocessing & Scaling
        X_scaled, feature_names = self.preprocessor.encode_and_scale(X_df, is_training=True)

        # Train-Test split with random_state=42
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y_series, test_size=test_size, random_state=self.random_state
        )

        if algorithms is None or len(algorithms) == 0:
            algorithms = ["decision_tree", "random_forest", "gradient_boosting"]
            if HAS_XGBOOST:
                algorithms.append("xgboost")
            algorithms.append("linear")

        trained_candidates = []

        for algo in algorithms:
            algo_params = (hyperparameters or {}).get(algo, {})
            model = self.instantiate_model(algo, actual_type, algo_params)

            # Measure training time
            t0_fit = time.perf_counter()
            model.fit(X_train, y_train)
            t1_fit = time.perf_counter()
            training_time = round(t1_fit - t0_fit, 4)

            # Measure prediction time on test set
            t0_pred = time.perf_counter()
            y_pred_test = model.predict(X_test)
            t1_pred = time.perf_counter()
            pred_time_ms = round((t1_pred - t0_pred) * 1000.0 / max(len(X_test), 1), 4)

            y_pred_train = model.predict(X_train)

            # Feature importances
            if hasattr(model, "feature_importances_"):
                importances = model.feature_importances_
            elif hasattr(model, "coef_"):
                coef = model.coef_
                importances = np.abs(coef[0]) if coef.ndim > 1 else np.abs(coef)
            else:
                importances = np.zeros(len(feature_names))

            feat_dict = {
                feature_names[i]: round(float(importances[i]), 4)
                for i in range(min(len(feature_names), len(importances)))
            }
            sorted_feat = dict(sorted(feat_dict.items(), key=lambda x: x[1], reverse=True)[:15])

            candidate_info = {
                "algorithm": algo,
                "model": model,
                "training_time": training_time,
                "prediction_time_ms": pred_time_ms,
                "y_train": y_train,
                "y_pred_train": y_pred_train,
                "y_test": y_test,
                "y_pred_test": y_pred_test,
                "feature_importance": sorted_feat,
                "hyperparameters": algo_params,
            }
            trained_candidates.append(candidate_info)

        logger.info("Training Completed: Successfully trained %d candidate models", len(trained_candidates))

        return {
            "prediction_type": actual_type,
            "target_variable": target_variable,
            "preprocessor": self.preprocessor,
            "label_encoder": label_encoder,
            "feature_names": feature_names,
            "candidates": trained_candidates,
            "split_info": {
                "train_size": len(X_train),
                "test_size": len(X_test),
                "total_samples": len(df),
                "test_ratio": test_size,
                "random_state": self.random_state
            }
        }

