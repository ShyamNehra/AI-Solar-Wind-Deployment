"""
Time Feature Engineering Engine for Time-Series Forecasting.
"""

from datetime import datetime
from typing import List, Dict, Any

class TimeSeriesFeatureEngine:
    """
    Extracts temporal and seasonal features from time-series timestamps:
    Year, Month, Day, Day of Month, Day of Year, Week Number, Quarter,
    Weekend Flag, Leap Year Flag, and Season.
    """

    def transform(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Applies time feature engineering to a list of historical/prediction records."""
        enriched = []
        for item in records:
            record = dict(item)
            date_val = record.get("date")
            
            if isinstance(date_val, str):
                try:
                    dt = datetime.strptime(date_val, "%Y-%m-%d")
                except ValueError:
                    try:
                        dt = datetime.fromisoformat(date_val)
                    except ValueError:
                        dt = datetime.now()
            elif isinstance(date_val, datetime):
                dt = date_val
            else:
                dt = datetime.now()

            year = dt.year
            month = dt.month
            day = dt.day
            day_of_year = dt.timetuple().tm_yday
            week_number = dt.isocalendar()[1]
            weekday = dt.weekday()  # 0=Monday, 6=Sunday
            quarter = (month - 1) // 3 + 1
            
            is_weekend = 1 if weekday >= 5 else 0
            is_leap = 1 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 0
            
            season = self._get_season(month)

            record.update({
                "year": year,
                "month": month,
                "day": day,
                "day_of_month": day,
                "day_of_year": day_of_year,
                "week_number": week_number,
                "quarter": quarter,
                "is_weekend": is_weekend,
                "is_leap_year": is_leap,
                "season": season,
            })
            
            enriched.append(record)

        return enriched

    @staticmethod
    def _get_season(month: int) -> str:
        """Determines seasonal category based on calendar month."""
        if month in (12, 1, 2):
            return "Winter"
        elif month in (3, 4, 5):
            return "Spring"
        elif month in (6, 7, 8):
            return "Monsoon/Summer"
        else:
            return "Autumn"
