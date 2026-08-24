"""
Feature & Target Variable Selector for ML Workflows.
"""

from typing import Tuple, List, Dict, Any, Union
import pandas as pd
import numpy as np

class FeatureSelector:
    """
    Selects numerical and categorical features for target prediction tasks.
    Determines prediction type (regression vs classification) automatically.
    """

    CLASSIFICATION_TARGETS = ["wind_class", "solar_class", "suitability_category", "category"]
    REGRESSION_TARGETS = ["solar_irradiance", "wind_speed", "suitability_score", "capacity_factor", "annual_energy_production"]

    def determine_target_type(self, df: pd.DataFrame, target_col: str) -> str:
        """
        Determines whether the target variable requires regression or classification.
        """
        if target_col in self.CLASSIFICATION_TARGETS:
            return "classification"
        if target_col in self.REGRESSION_TARGETS:
            return "regression"

        if target_col in df.columns:
            dtype = df[target_col].dtype
            if dtype == object or dtype.name == "category" or str(dtype) == "string":
                return "classification"
            if len(df[target_col].unique()) < 10 and not np.issubdtype(dtype, np.floating):
                return "classification"

        return "regression"

    def split_features_and_target(
        self, df: pd.DataFrame, target_col: str = "solar_irradiance"
    ) -> Tuple[pd.DataFrame, pd.Series, str]:
        """
        Separates feature matrix (X_df) and target vector (y_series).
        """
        if target_col not in df.columns:
            # Fallback target if requested column is not in dataframe
            if "solar_irradiance" in df.columns:
                target_col = "solar_irradiance"
            elif "wind_speed" in df.columns:
                target_col = "wind_speed"
            else:
                target_col = df.columns[-1]

        target_type = self.determine_target_type(df, target_col)
        y = df[target_col].copy()
        X = df.drop(columns=[target_col], errors="ignore")

        return X, y, target_type
