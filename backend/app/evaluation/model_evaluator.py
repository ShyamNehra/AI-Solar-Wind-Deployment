import numpy as np
import pandas as pd
from typing import Dict, Any, List
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


class ModelEvaluator:
    """
    Evaluates trained regression models for the forecasting pipeline
    and generates structured comparison reports.
    """

    @staticmethod
    def calculate_regression_metrics(y_true: np.ndarray, y_pred: np.ndarray, model_name: str) -> Dict[str, Any]:
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        r2 = r2_score(y_true, y_pred)

        # Avoid zero-division for MAPE
        non_zero_mask = y_true != 0
        mape = np.mean(np.abs((y_true[non_zero_mask] - y_pred[non_zero_mask]) / y_true[non_zero_mask])) * 100

        return {
            "model_name": model_name,
            "mae": round(float(mae), 4),
            "rmse": round(float(rmse), 4),
            "mape_percent": round(float(mape), 2),
            "r2_score": round(float(r2), 4)
        }

    def generate_comparison_table(self, evaluations: List[Dict[str, Any]]) -> pd.DataFrame:
        """Converts a list of evaluation metric dictionaries into a clean DataFrame."""
        df = pd.DataFrame(evaluations)
        df.rename(columns={
            "model_name": "Model",
            "mae": "MAE (MWh)",
            "rmse": "RMSE (MWh)",
            "mape_percent": "MAPE (%)",
            "r2_score": "R² Score"
        }, inplace=True)
        return df