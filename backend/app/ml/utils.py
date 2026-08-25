"""
Machine Learning Utilities.
"""

from datetime import datetime
from typing import Dict, Any

def extract_temporal_features(dt: datetime = None) -> Dict[str, Any]:
    """
    Extracts temporal and calendar features from a datetime object.
    """
    if dt is None:
        dt = datetime.now()

    month = dt.month
    day = dt.day
    week_num = dt.isocalendar()[1]
    day_of_year = dt.timetuple().tm_yday
    quarter = (month - 1) // 3 + 1
    weekend = 1 if dt.weekday() in [5, 6] else 0
    leap_year = 1 if (dt.year % 4 == 0 and (dt.year % 100 != 0 or dt.year % 400 == 0)) else 0

    if month in [12, 1, 2]:
        season = "Winter"
    elif month in [3, 4, 5]:
        season = "Spring"
    elif month in [6, 7, 8]:
        season = "Summer"
    else:
        season = "Autumn"

    return {
        "season": season,
        "month": month,
        "day": day,
        "week_number": week_num,
        "day_of_year": day_of_year,
        "quarter": quarter,
        "weekend_flag": weekend,
        "leap_year_flag": leap_year,
    }
