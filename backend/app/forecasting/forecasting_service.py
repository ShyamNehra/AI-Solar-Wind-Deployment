class ForecastingService:
    """
    Main forecasting service.

    This service coordinates:
    - Solar forecasting
    - Wind forecasting
    - Hybrid forecasting
    """

    def __init__(self):
        pass

    def solar_forecast(self, data):
        """
        Generate solar forecast.
        """
        return {
            "forecast_type": "Solar",
            "status": "Ready for implementation"
        }

    def wind_forecast(self, data):
        """
        Generate wind forecast.
        """
        return {
            "forecast_type": "Wind",
            "status": "Ready for implementation"
        }

    def hybrid_forecast(self, data):
        """
        Generate hybrid forecast.
        """
        return {
            "forecast_type": "Hybrid",
            "status": "Ready for implementation"
        }
"""
High-level Forecasting Orchestration Service.
"""

from typing import List, Dict, Any, Optional
from app.forecasting.data_loader import TimeSeriesDataLoader
from app.forecasting.feature_engineering import TimeSeriesFeatureEngine
from app.forecasting.solar_forecast import SolarForecaster
from app.forecasting.wind_forecast import WindForecaster
from app.forecasting.hybrid_forecast import HybridForecaster

class ForecastingService:
    """
    Central forecasting service executing full end-to-end pipeline:
    1. Historical NASA POWER Data Loading
    2. Missing Value Imputation & Sorting
    3. Temporal & Seasonal Feature Engineering
    4. Model Execution (Solar, Wind, Hybrid)
    5. Output Generation
    """

    def __init__(self):
        self.data_loader = TimeSeriesDataLoader()
        self.feature_engine = TimeSeriesFeatureEngine()
        self.solar_forecaster = SolarForecaster()
        self.wind_forecaster = WindForecaster()
        self.hybrid_forecaster = HybridForecaster()

    def run_forecast(
        self,
        forecast_type: str = "solar",  # 'solar' | 'wind' | 'hybrid'
        latitude: float = 26.9124,
        longitude: float = 75.7873,
        horizon_days: int = 7,
        installed_capacity_mw: float = 50.0,
        historical_data: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Executes complete forecasting pipeline for target coordinates and mode.
        """
        # Step 1 & 2: Load historical observations & clean/sort by date
        raw_records = self.data_loader.load_historical_data(
            latitude=latitude,
            longitude=longitude,
            days=30,
            raw_data=historical_data
        )

        # Step 3: Extract time features (year, month, day, season, weekend, etc.)
        enriched_records = self.feature_engine.transform(raw_records)

        # Step 4 & 5: Run model prediction
        ftype = (forecast_type or "solar").lower()

        if ftype == "wind":
            result = self.wind_forecaster.forecast(
                historical_records=enriched_records,
                horizon_days=horizon_days,
                installed_capacity_mw=installed_capacity_mw
            )
        elif ftype == "hybrid":
            solar_cap = installed_capacity_mw * 0.6
            wind_cap = installed_capacity_mw * 0.4
            result = self.hybrid_forecaster.forecast(
                historical_records=enriched_records,
                horizon_days=horizon_days,
                solar_capacity_mw=solar_cap,
                wind_capacity_mw=wind_cap
            )
        else:  # Default: solar
            result = self.solar_forecaster.forecast(
                historical_records=enriched_records,
                horizon_days=horizon_days,
                installed_capacity_mw=installed_capacity_mw
            )

        # Attach metadata
        result["location"] = {
            "latitude": latitude,
            "longitude": longitude,
            "installed_capacity_mw": installed_capacity_mw
        }
        result["historical_samples_count"] = len(enriched_records)

        return result
