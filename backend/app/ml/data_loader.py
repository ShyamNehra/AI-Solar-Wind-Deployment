"""
Dataset Builder & Loader for Machine Learning Baseline Training.
"""

from typing import List, Dict, Any, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.feature_engineering.feature_builder import FeatureBuilder

class MLDataLoader:
    """
    Gathers and prepares feature records from DB models (FeatureStore, Feature, Site)
    and physical domain functions to create a training dataset.
    """

    def __init__(self):
        self.feature_builder = FeatureBuilder()

    def generate_training_dataset(self, db: Session = None, num_samples: int = 250) -> pd.DataFrame:
        """
        Creates a DataFrame containing all required engineered features:
        - Solar Irradiance, Wind Speed, Temperature, Humidity, Terrain Score, Slope,
          Elevation, Road Distance, Grid Distance (Substation), Accessibility,
          Capacity Factor, Environmental Score, Infrastructure Score, Lat/Lon,
          Season, Month, Day, Week Number, Day Of Year, Quarter, Weekend Flag,
          Leap Year Flag, Wind Class, Solar Class.
        """
        records = []

        # 1. Pull existing records from DB if available
        if db:
            try:
                from app.models.feature_store import FeatureStore
                from app.models.site import Site

                fs_records = db.query(FeatureStore).all()
                for fs in fs_records:
                    rec = self._map_feature_store_record(fs)
                    if rec:
                        records.append(rec)
            except Exception as e:
                print(f"Notice: Failed to query FeatureStore for ML training: {e}")

        # 2. If DB records are insufficient, generate a domain-valid synthetic dataset
        if len(records) < num_samples:
            needed = num_samples - len(records)
            synthetic_records = self._generate_synthetic_dataset(needed)
            records.extend(synthetic_records)

        df = pd.DataFrame(records)
        return df

    def _map_feature_store_record(self, fs) -> Dict[str, Any]:
        lat = getattr(fs, 'latitude', 26.9124)
        lon = getattr(fs, 'longitude', 75.7873)
        dt = getattr(fs, 'created_at', None) or datetime.now()

        # Compute temporal features
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

        solar = getattr(fs, 'solar_irradiance', 5.2) or 5.2
        wind = getattr(fs, 'wind_speed', 6.5) or 6.5
        elev = getattr(fs, 'elevation', 250.0) or 250.0
        slope = getattr(fs, 'slope', 2.0) or 2.0
        road = getattr(fs, 'road_distance', 4.0) or 4.0
        substation = getattr(fs, 'substation_distance', 8.0) or 8.0

        wind_class = "Excellent" if wind > 8.5 else "Good" if wind > 6.0 else "Moderate" if wind > 4.5 else "Poor"
        solar_class = "High" if solar > 5.5 else "Medium" if solar > 4.0 else "Low"

        accessibility = max(0.0, min(100.0, 100.0 - road * 4.0 - substation * 2.0))
        terrain_score = max(0.0, min(100.0, 100.0 - slope * 3.5 - (elev / 50.0)))
        env_score = max(0.0, min(100.0, 85.0 - (slope * 2.0)))
        infra_score = max(0.0, min(100.0, 90.0 - road * 3.0 - substation * 2.5))
        capacity_factor = round(min(45.0, max(15.0, solar * 3.0 + wind * 2.2)), 2)

        return {
            "latitude": lat,
            "longitude": lon,
            "solar_irradiance": solar,
            "wind_speed": wind,
            "temperature": getattr(fs, 'temperature', 25.0) or 25.0,
            "humidity": getattr(fs, 'humidity', 50.0) or 50.0,
            "elevation": elev,
            "slope": slope,
            "road_distance": road,
            "substation_distance": substation,
            "accessibility": accessibility,
            "terrain_score": terrain_score,
            "environmental_score": env_score,
            "infrastructure_score": infra_score,
            "capacity_factor": capacity_factor,
            "wind_class": wind_class,
            "solar_class": solar_class,
            "season": season,
            "month": month,
            "day": day,
            "week_number": week_num,
            "day_of_year": day_of_year,
            "quarter": quarter,
            "weekend_flag": weekend,
            "leap_year_flag": leap_year,
            "suitability_score": getattr(fs, 'suitability_score', 75.0) or 75.0,
        }

    def _generate_synthetic_dataset(self, n: int) -> List[Dict[str, Any]]:
        np.random.seed(42)
        base_date = datetime(2025, 1, 1)
        records = []

        for i in range(n):
            lat = float(np.random.uniform(8.0, 32.0))
            lon = float(np.random.uniform(68.0, 88.0))
            dt = base_date + timedelta(days=i % 365, hours=int(np.random.uniform(0, 24)))

            month = dt.month
            day = dt.day
            week_num = dt.isocalendar()[1]
            day_of_year = dt.timetuple().tm_yday
            quarter = (month - 1) // 3 + 1
            weekend = 1 if dt.weekday() in [5, 6] else 0
            leap_year = 0

            if month in [12, 1, 2]:
                season = "Winter"
                seasonal_solar_mult = 0.8
            elif month in [3, 4, 5]:
                season = "Spring"
                seasonal_solar_mult = 1.15
            elif month in [6, 7, 8]:
                season = "Summer"
                seasonal_solar_mult = 1.25
            else:
                season = "Autumn"
                seasonal_solar_mult = 0.95

            base_solar = float(np.random.normal(5.0, 1.2)) * seasonal_solar_mult
            solar = max(1.0, min(8.5, round(base_solar, 2)))

            base_wind = float(np.random.normal(6.2, 2.0))
            wind = max(1.5, min(14.0, round(base_wind, 2)))

            temp = round(float(np.random.normal(27.0 - (lat - 20.0) * 0.4, 5.0)), 1)
            temp = max(5.0, min(48.0, temp))

            humidity = round(float(np.random.normal(55.0, 15.0)), 1)
            humidity = max(10.0, min(95.0, humidity))

            elev = round(float(np.random.uniform(50.0, 1200.0)), 1)
            slope = round(float(np.random.exponential(3.0)), 1)
            slope = min(45.0, slope)

            road = round(float(np.random.uniform(0.5, 25.0)), 2)
            substation = round(float(np.random.uniform(1.0, 45.0)), 2)

            accessibility = round(max(0.0, min(100.0, 100.0 - road * 3.0 - substation * 1.5)), 1)
            terrain_score = round(max(0.0, min(100.0, 100.0 - slope * 2.8 - (elev / 60.0))), 1)
            env_score = round(max(0.0, min(100.0, 90.0 - slope * 1.5 - np.random.uniform(0, 15))), 1)
            infra_score = round(max(0.0, min(100.0, 95.0 - road * 2.5 - substation * 1.8)), 1)

            capacity_factor = round(min(52.0, max(12.0, solar * 3.2 + wind * 2.4 - slope * 0.3)), 2)

            wind_class = "Excellent" if wind > 8.5 else "Good" if wind > 6.0 else "Moderate" if wind > 4.0 else "Poor"
            solar_class = "High" if solar > 5.5 else "Medium" if solar > 4.0 else "Low"

            suitability = round(min(98.0, max(20.0, (solar * 7.0 + wind * 5.0 + terrain_score * 0.3 + infra_score * 0.25))), 1)

            records.append({
                "latitude": lat,
                "longitude": lon,
                "solar_irradiance": solar,
                "wind_speed": wind,
                "temperature": temp,
                "humidity": humidity,
                "elevation": elev,
                "slope": slope,
                "road_distance": road,
                "substation_distance": substation,
                "accessibility": accessibility,
                "terrain_score": terrain_score,
                "environmental_score": env_score,
                "infrastructure_score": infra_score,
                "capacity_factor": capacity_factor,
                "wind_class": wind_class,
                "solar_class": solar_class,
                "season": season,
                "month": month,
                "day": day,
                "week_number": week_num,
                "day_of_year": day_of_year,
                "quarter": quarter,
                "weekend_flag": weekend,
                "leap_year_flag": leap_year,
                "suitability_score": suitability,
            })

        return records
