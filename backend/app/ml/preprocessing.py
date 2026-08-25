"""
Preprocessor Engine for Feature Cleaning, Outlier Filtering, Encoding & Scaling.
"""

import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Any, Optional
from sklearn.preprocessing import StandardScaler

class MLPreprocessor:
    """
    Reusable data preprocessor that cleans raw feature dataframes:
    1. Removes duplicate rows.
    2. Filters out physically invalid values (negative wind/irradiance, out-of-range lat/lon).
    3. Handles missing values using median/mode imputation.
    4. Handles extreme outliers using clipping/IQR thresholds.
    5. Performs categorical encoding.
    6. Fits & applies feature scaling using StandardScaler.
    """

    CATEGORICAL_COLS = ["season", "wind_class", "solar_class"]
    NUMERICAL_COLS = [
        "latitude", "longitude", "solar_irradiance", "wind_speed",
        "temperature", "humidity", "elevation", "slope",
        "road_distance", "substation_distance", "accessibility",
        "terrain_score", "environmental_score", "infrastructure_score",
        "capacity_factor", "month", "day", "week_number",
        "day_of_year", "quarter", "weekend_flag", "leap_year_flag"
    ]

    def __init__(self):
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.feature_columns: List[str] = []
        self.impute_values: Dict[str, Any] = {}

    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cleans input dataframe: removes duplicates, imputes missing values,
        and caps extreme outliers.
        """
        if df.empty:
            return df

        cleaned = df.copy()

        # 1. Remove duplicate rows
        cleaned = cleaned.drop_duplicates()

        # 2. Filter out physically impossible or out-of-bound values
        if "latitude" in cleaned.columns:
            cleaned = cleaned[(cleaned["latitude"] >= -90.0) & (cleaned["latitude"] <= 90.0)]
        if "longitude" in cleaned.columns:
            cleaned = cleaned[(cleaned["longitude"] >= -180.0) & (cleaned["longitude"] <= 180.0)]
        if "solar_irradiance" in cleaned.columns:
            cleaned.loc[cleaned["solar_irradiance"] < 0, "solar_irradiance"] = np.nan
        if "wind_speed" in cleaned.columns:
            cleaned.loc[cleaned["wind_speed"] < 0, "wind_speed"] = np.nan

        # 3. Impute missing numerical values (median) and categorical values (mode)
        for col in self.NUMERICAL_COLS:
            if col in cleaned.columns:
                if col not in self.impute_values:
                    self.impute_values[col] = float(cleaned[col].median()) if not cleaned[col].dropna().empty else 0.0
                cleaned[col] = cleaned[col].fillna(self.impute_values[col])

        for col in self.CATEGORICAL_COLS:
            if col in cleaned.columns:
                if col not in self.impute_values:
                    mode_val = cleaned[col].mode()
                    self.impute_values[col] = str(mode_val[0]) if not mode_val.empty else "Normal"
                cleaned[col] = cleaned[col].fillna(self.impute_values[col])

        # 4. Cap extreme outliers for key physical continuous variables using IQR
        outlier_cols = ["solar_irradiance", "wind_speed", "slope", "road_distance", "substation_distance"]
        for col in outlier_cols:
            if col in cleaned.columns and len(cleaned) > 10:
                q1 = cleaned[col].quantile(0.01)
                q3 = cleaned[col].quantile(0.99)
                cleaned[col] = cleaned[col].clip(lower=q1, upper=q3)

        return cleaned

    def encode_and_scale(
        self, df: pd.DataFrame, is_training: bool = True
    ) -> Tuple[np.ndarray, List[str]]:
        """
        One-hot encodes categorical columns and applies StandardScaler to numerical columns.
        Returns scaled feature matrix and list of feature column names.
        """
        cleaned = self.clean_dataframe(df)

        # Categorical encoding (one-hot or ordinal)
        encoded_df = pd.get_dummies(
            cleaned,
            columns=[c for c in self.CATEGORICAL_COLS if c in cleaned.columns],
            drop_first=False
        )

        # Select numerical/encoded feature columns (exclude target labels if present)
        feature_cols = [c for c in encoded_df.columns if c not in ["suitability_score", "target", "id"]]

        if is_training or not self.is_fitted:
            self.feature_columns = feature_cols
            X_scaled = self.scaler.fit_transform(encoded_df[feature_cols])
            self.is_fitted = True
        else:
            # Align test/predict columns with training feature columns
            aligned_df = pd.DataFrame(0, index=encoded_df.index, columns=self.feature_columns)
            for c in self.feature_columns:
                if c in encoded_df.columns:
                    aligned_df[c] = encoded_df[c]
            X_scaled = self.scaler.transform(aligned_df)

        return X_scaled, self.feature_columns
