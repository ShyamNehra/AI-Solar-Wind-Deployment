"""
Model Evaluation Engine for Scikit-Learn Random Forest Regressor & Classifier.
"""

from typing import Dict, Any, List
import numpy as np
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

class MLEvaluator:
    """
    Evaluates trained Scikit-learn models and generates structured evaluation reports.
    """

    def evaluate_regression(
        self, y_true: np.ndarray, y_pred: np.ndarray, cv_scores: np.ndarray = None
    ) -> Dict[str, Any]:
        """
        Computes regression evaluation metrics: MAE, MSE, RMSE, R² Score, and MAPE.
        """
        y_true_arr = np.array(y_true, dtype=float)
        y_pred_arr = np.array(y_pred, dtype=float)

        mae = float(mean_absolute_error(y_true_arr, y_pred_arr))
        mse = float(mean_squared_error(y_true_arr, y_pred_arr))
        rmse = float(np.sqrt(mse))
        r2 = float(r2_score(y_true_arr, y_pred_arr))

        # Safe calculation of Mean Absolute Percentage Error (MAPE)
        nonzero_mask = np.abs(y_true_arr) > 1e-6
        if np.any(nonzero_mask):
            mape = float(np.mean(np.abs((y_true_arr[nonzero_mask] - y_pred_arr[nonzero_mask]) / y_true_arr[nonzero_mask])) * 100.0)
        else:
            mape = 0.0

        cv_mean = float(np.mean(cv_scores)) if cv_scores is not None and len(cv_scores) > 0 else r2

        return {
            "prediction_type": "regression",
            "mae": round(mae, 4),
            "mse": round(mse, 4),
            "rmse": round(rmse, 4),
            "r2_score": round(r2, 4),
            "mape": round(mape, 4),
            "cross_validation_score": round(cv_mean, 4),
            "sample_size": len(y_true_arr),
        }

    def evaluate_classification(
        self, y_true: np.ndarray, y_pred: np.ndarray, cv_scores: np.ndarray = None
    ) -> Dict[str, Any]:
        """
        Computes classification evaluation metrics: Accuracy, Precision, Recall, F1 Score, Confusion Matrix.
        """
        accuracy = float(accuracy_score(y_true, y_pred))
        precision = float(precision_score(y_true, y_pred, average="weighted", zero_division=0))
        recall = float(recall_score(y_true, y_pred, average="weighted", zero_division=0))
        f1 = float(f1_score(y_true, y_pred, average="weighted", zero_division=0))
        cm = confusion_matrix(y_true, y_pred).tolist()

        cv_mean = float(np.mean(cv_scores)) if cv_scores is not None and len(cv_scores) > 0 else accuracy

        return {
            "prediction_type": "classification",
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "confusion_matrix": cm,
            "cross_validation_score": round(cv_mean, 4),
            "sample_size": len(y_true),
        }
