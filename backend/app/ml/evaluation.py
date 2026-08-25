"""
Model Evaluation Engine for Regression, Classification, and Forecasting models.
Calculates MAE, RMSE, R², Accuracy, Precision, Recall, F1, MAPE, training/prediction speed, and model size.
Generates structured comparison tables.
"""

import io
import pickle
import joblib
import logging
from pathlib import Path
from typing import Dict, Any, List
import numpy as np
import pandas as pd
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

logger = logging.getLogger("ml.evaluation")

ALGORITHM_DISPLAY_NAMES = {
    "decision_tree": "Decision Tree",
    "random_forest": "Random Forest",
    "gradient_boosting": "Gradient Boosting",
    "xgboost": "XGBoost",
    "extra_trees": "Extra Trees",
    "linear": "Linear Model",
    "linear_regression": "Linear Regression",
    "logistic_regression": "Logistic Regression",
}

COMPLEXITY_LABELS = {
    "linear": "Low (Linear Model)",
    "linear_regression": "Low (Linear Model)",
    "logistic_regression": "Low (Linear Model)",
    "decision_tree": "Low-Medium (Decision Tree)",
    "random_forest": "Medium (Random Forest, 100 Trees)",
    "gradient_boosting": "High (Gradient Boosting, 100 Trees)",
    "xgboost": "High (XGBoost)",
    "extra_trees": "Medium-High (Extra Trees)",
}


class ModelEvaluator:
    """
    Evaluates candidate models across regression, classification, and forecasting metrics.
    Measures model size and speed to create structured comparison tables and CSV exports.
    """

    def compute_model_size_kb(self, model: Any) -> float:
        """
        Calculates exact serialized in-memory byte size of the model estimator in KB.
        """
        try:
            buf = io.BytesIO()
            joblib.dump(model, buf)
            return round(buf.tell() / 1024.0, 2)
        except Exception:
            try:
                raw_bytes = pickle.dumps(model)
                return round(len(raw_bytes) / 1024.0, 2)
            except Exception:
                return 0.0

    def evaluate_regression(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """
        Computes regression metrics: MAE, RMSE, R² Score, MAPE.
        """
        y_true_arr = np.array(y_true, dtype=float)
        y_pred_arr = np.array(y_pred, dtype=float)

        mae = float(mean_absolute_error(y_true_arr, y_pred_arr))
        mse = float(mean_squared_error(y_true_arr, y_pred_arr))
        rmse = float(np.sqrt(mse))
        r2 = float(r2_score(y_true_arr, y_pred_arr))

        nonzero_mask = np.abs(y_true_arr) > 1e-6
        if np.any(nonzero_mask):
            mape = float(np.mean(np.abs((y_true_arr[nonzero_mask] - y_pred_arr[nonzero_mask]) / y_true_arr[nonzero_mask])) * 100.0)
        else:
            mape = 0.0

        return {
            "mae": round(mae, 4),
            "mse": round(mse, 4),
            "rmse": round(rmse, 4),
            "r2": round(r2, 4),
            "r2_score": round(r2, 4),
            "mape": round(mape, 4)
        }

    def evaluate_classification(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
        """
        Computes classification metrics: Accuracy, Precision, Recall, F1 Score.
        """
        accuracy = float(accuracy_score(y_true, y_pred))
        precision = float(precision_score(y_true, y_pred, average="weighted", zero_division=0))
        recall = float(recall_score(y_true, y_pred, average="weighted", zero_division=0))
        f1 = float(f1_score(y_true, y_pred, average="weighted", zero_division=0))
        cm = confusion_matrix(y_true, y_pred).tolist()

        return {
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "confusion_matrix": cm
        }

    def create_comparison_table(
        self,
        candidates: List[Dict[str, Any]],
        prediction_type: str = "regression"
    ) -> List[Dict[str, Any]]:
        """
        Evaluates all trained candidate models and generates structured comparison table.
        Saves comparison_results.csv inside backend/models/.
        """
        table = []
        for cand in candidates:
            algo_key = cand["algorithm"]
            model = cand["model"]
            training_time = cand.get("training_time", 0.0)
            pred_time_ms = cand.get("prediction_time_ms", 0.0)
            size_kb = self.compute_model_size_kb(model)
            complexity_str = COMPLEXITY_LABELS.get(algo_key, "Medium (Ensemble)")

            display_name = ALGORITHM_DISPLAY_NAMES.get(algo_key, algo_key.replace("_", " ").title())
            if prediction_type == "regression":
                if "Regressor" not in display_name:
                    display_name += " Regressor"
            elif prediction_type == "classification":
                if "Classifier" not in display_name:
                    display_name += " Classifier"

            if prediction_type == "classification":
                metrics = self.evaluate_classification(cand["y_test"], cand["y_pred_test"])
                train_metrics = self.evaluate_classification(cand["y_train"], cand["y_pred_train"])
                diff = train_metrics["accuracy"] - metrics["accuracy"]
                behavior_str = "Overfitting" if diff > 0.15 else "Underfitting" if metrics["accuracy"] < 0.6 else "Generalizing Well"

                row = {
                    "Model Name": display_name,
                    "model": display_name,
                    "algorithm": algo_key,
                    "Training Time": training_time,
                    "training_time": training_time,
                    "Prediction Time": pred_time_ms,
                    "prediction_time": pred_time_ms,
                    "MAE": "N/A",
                    "mae": 0.0,
                    "RMSE": "N/A",
                    "rmse": 0.0,
                    "R²": "N/A",
                    "r2": 0.0,
                    "r2_score": 0.0,
                    "Accuracy": metrics["accuracy"],
                    "accuracy": metrics["accuracy"],
                    "Precision": metrics["precision"],
                    "precision": metrics["precision"],
                    "Recall": metrics["recall"],
                    "recall": metrics["recall"],
                    "F1": metrics["f1_score"],
                    "f1_score": metrics["f1_score"],
                    "MAPE": "N/A",
                    "mape": 0.0,
                    "Complexity": complexity_str,
                    "Memory Size": f"{size_kb} KB",
                    "model_size": f"{size_kb} KB",
                    "model_size_kb": size_kb,
                    "Inference Speed": f"{pred_time_ms:.2f} ms",
                    "metrics": metrics,
                    "validation_metrics": metrics,
                    "train_metrics": train_metrics,
                    "test_metrics": metrics,
                    "behavior_analysis": behavior_str,
                    "feature_importance": cand.get("feature_importance", {})
                }
            else: # Regression / Forecasting
                metrics = self.evaluate_regression(cand["y_test"], cand["y_pred_test"])
                train_metrics = self.evaluate_regression(cand["y_train"], cand["y_pred_train"])
                r2_diff = train_metrics["r2"] - metrics["r2"]
                behavior_str = "Overfitting" if r2_diff > 0.20 else "Underfitting" if metrics["r2"] < 0.4 else "Generalizing Well"

                row = {
                    "Model Name": display_name,
                    "model": display_name,
                    "algorithm": algo_key,
                    "Training Time": training_time,
                    "training_time": training_time,
                    "Prediction Time": pred_time_ms,
                    "prediction_time": pred_time_ms,
                    "MAE": metrics["mae"],
                    "mae": metrics["mae"],
                    "RMSE": metrics["rmse"],
                    "rmse": metrics["rmse"],
                    "R²": metrics["r2"],
                    "r2": metrics["r2"],
                    "r2_score": metrics["r2_score"],
                    "Accuracy": "N/A",
                    "accuracy": 0.0,
                    "Precision": "N/A",
                    "precision": 0.0,
                    "Recall": "N/A",
                    "recall": 0.0,
                    "F1": "N/A",
                    "f1_score": 0.0,
                    "MAPE": metrics["mape"],
                    "mape": metrics["mape"],
                    "Complexity": complexity_str,
                    "Memory Size": f"{size_kb} KB",
                    "model_size": f"{size_kb} KB",
                    "model_size_kb": size_kb,
                    "Inference Speed": f"{pred_time_ms:.2f} ms",
                    "metrics": metrics,
                    "validation_metrics": metrics,
                    "train_metrics": train_metrics,
                    "test_metrics": metrics,
                    "behavior_analysis": behavior_str,
                    "feature_importance": cand.get("feature_importance", {})
                }

            cand["metrics"] = metrics
            cand["train_metrics"] = train_metrics
            cand["comparison_row"] = row
            table.append(row)

        # Save comparison_results.csv to backend/models/
        try:
            models_dir = Path(__file__).resolve().parent.parent.parent / "models"
            models_dir.mkdir(parents=True, exist_ok=True)
            csv_path = models_dir / "comparison_results.csv"

            # Create clean CSV dataframe with user-facing headers
            csv_rows = []
            for r in table:
                csv_rows.append({
                    "Model Name": r["Model Name"],
                    "Training Time (s)": r["Training Time"],
                    "Prediction Time (ms)": r["Prediction Time"],
                    "MAE": r["MAE"],
                    "RMSE": r["RMSE"],
                    "R² Score": r["R²"],
                    "Accuracy": r["Accuracy"],
                    "Precision": r["Precision"],
                    "Recall": r["Recall"],
                    "F1 Score": r["F1"],
                    "MAPE": r["MAPE"],
                    "Complexity": r["Complexity"],
                    "Memory Size": r["Memory Size"],
                    "Inference Speed": r["Inference Speed"],
                })
            pd.DataFrame(csv_rows).to_csv(csv_path, index=False)
            logger.info("Saved comparison table to '%s'", csv_path)
        except Exception as e:
            logger.warning("Could not save comparison_results.csv: %s", e)

        logger.info("Evaluation Completed: Generated comparison table for %d models", len(table))
        return table

