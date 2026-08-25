"""
Forecasting utilities for model metrics and data transformations.
"""

import math
from typing import List, Dict, Any, Union

def calculate_mae(actual: List[float], predicted: List[float]) -> float:
    """Calculate Mean Absolute Error."""
    if not actual or not predicted or len(actual) != len(predicted):
        return 0.0
    errors = [abs(a - p) for a, p in zip(actual, predicted)]
    return float(sum(errors) / len(errors))

def calculate_rmse(actual: List[float], predicted: List[float]) -> float:
    """Calculate Root Mean Squared Error."""
    if not actual or not predicted or len(actual) != len(predicted):
        return 0.0
    sq_errors = [(a - p) ** 2 for a, p in zip(actual, predicted)]
    return float(math.sqrt(sum(sq_errors) / len(sq_errors)))

def calculate_mape(actual: List[float], predicted: List[float]) -> float:
    """Calculate Mean Absolute Percentage Error."""
    if not actual or not predicted or len(actual) != len(predicted):
        return 0.0
    pct_errors = [abs((a - p) / a) for a, p in zip(actual, predicted) if a != 0]
    if not pct_errors:
        return 0.0
    return float((sum(pct_errors) / len(pct_errors)) * 100.0)

def format_confidence_interval(prediction: float, confidence_pct: float = 95.0, error_std: float = 0.05) -> Dict[str, float]:
    """Generate upper and lower bounds for a forecast point."""
    margin = prediction * error_std * 1.96
    return {
        "prediction": round(prediction, 4),
        "lower_bound": round(max(0.0, prediction - margin), 4),
        "upper_bound": round(prediction + margin, 4),
        "confidence_level": confidence_pct
    }
