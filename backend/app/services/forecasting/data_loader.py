import pandas as pd
from typing import Union, List, Dict

class TimeSeriesDataLoader:
    def __init__(self, data: Union[str, List[Dict], pd.DataFrame]):
        self.raw_data = data

    def load_clean_data(self, date_column: str = "date") -> pd.DataFrame:
        """Loads historical energy/weather data and enforces chronological order."""
        if isinstance(self.raw_data, str):
            df = pd.read_csv(self.raw_data)
        elif isinstance(self.raw_data, list):
            df = pd.DataFrame(self.raw_data)
        else:
            df = self.raw_data.copy()

        # Enforce datetime formatting & sort chronologically
        df[date_column] = pd.to_datetime(df[date_column])
        df = df.sort_values(by=date_column).reset_index(drop=True)
        
        # Fill minor missing data points
        df = df.ffill().bfill()
        return df