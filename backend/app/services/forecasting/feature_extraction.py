import pandas as pd

class TemporalFeatureExtractor:
    @staticmethod
    def extract_time_features(df: pd.DataFrame, date_column: str = "date") -> pd.DataFrame:
        """Extracts key calendar attributes for time-series models."""
        df = df.copy()
        if not pd.api.types.is_datetime64_any_dtype(df[date_column]):
            df[date_column] = pd.to_datetime(df[date_column])

        df["year"] = df[date_column].dt.year
        df["month"] = df[date_column].dt.month
        df["day"] = df[date_column].dt.day
        df["day_of_year"] = df[date_column].dt.dayofyear
        df["week_of_year"] = df[date_column].dt.isocalendar().week.astype(int)
        df["day_of_week"] = df[date_column].dt.dayofweek
        
        return df