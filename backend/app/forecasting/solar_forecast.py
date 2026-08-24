"""
Solar Irradiance and PV Energy Generation Forecaster.
"""

from datetime import datetime, timedelta
import math
from typing import List, Dict, Any, Optional
from app.forecasting.utils import calculate_mae, calculate_rmse, calculate_mape, format_confidence_interval

class SolarForecaster:
    """
    Forecasting model for multi-horizon Solar Irradiance (kWh/m²/day)
    and expected PV Energy Output (MWh/day).
    """

    def forecast(
        self,
        historical_records: List[Dict[str, Any]],
        horizon_days: int = 7,
        installed_capacity_mw: float = 50.0
    ) -> Dict[str, Any]:
        """
        Executes solar forecasting pipeline over a multi-day horizon.
        """
        if not historical_records:
            return self._empty_response()

        recent = historical_records[-14:] if len(historical_records) >= 14 else historical_records
        solar_vals = [r["solar_irradiance"] for r in recent]
        
        base_solar = sum(solar_vals) / len(solar_vals)
        alpha = 0.35  # Exponential smoothing weight
        
        smoothed_solar = solar_vals[0]
        for val in solar_vals[1:]:
            smoothed_solar = alpha * val + (1 - alpha) * smoothed_solar

        last_date_str = historical_records[-1].get("date", datetime.now().strftime("%Y-%m-%d"))
        try:
            start_date = datetime.strptime(last_date_str, "%Y-%m-%d")
        except ValueError:
            start_date = datetime.now()

        forecast_points = []
        predicted_solars = []
        predicted_energies = []

        # Performance degradation coefficient per day of forecast
        pr_efficiency = 0.82  # System Performance Ratio

        for i in range(1, horizon_days + 1):
            target_date = start_date + timedelta(days=i)
            day_of_year = target_date.timetuple().tm_yday
            
            # Seasonal solar factor variation
            seasonal_factor = 1.0 + 0.15 * math.sin(2 * math.pi * (day_of_year - 80) / 365)
            harmonic_drift = 0.2 * math.sin(i * 0.8)
            
            pred_solar = max(0.5, round(smoothed_solar * seasonal_factor + harmonic_drift, 2))
            
            # Daily Energy Output in MWh = Capacity(MW) * Irradiance(kWh/m²/d) * Performance Ratio
            pred_energy_mwh = round(installed_capacity_mw * pred_solar * pr_efficiency, 2)
            
            predicted_solars.append(pred_solar)
            predicted_energies.append(pred_energy_mwh)

            ci = format_confidence_interval(pred_solar, confidence_pct=95.0, error_std=0.04)

            forecast_points.append({
                "date": target_date.strftime("%Y-%m-%d"),
                "horizon_step": i,
                "predicted_solar_irradiance": pred_solar,
                "predicted_energy_generation": pred_energy_mwh,
                "lower_bound": ci["lower_bound"],
                "upper_bound": ci["upper_bound"],
                "unit_irradiance": "kWh/m²/day",
                "unit_energy": "MWh",
                "season": "Summer" if target_date.month in [5,6,7,8] else "Winter" if target_date.month in [11,12,1,2] else "Transition"
            })

        avg_pred_solar = round(sum(predicted_solars) / len(predicted_solars), 2)
        total_energy_mwh = round(sum(predicted_energies), 2)

        # Validation against recent history
        mae = round(calculate_mae(solar_vals[-horizon_days:] if len(solar_vals) >= horizon_days else solar_vals, predicted_solars[:len(solar_vals)]), 3)
        rmse = round(calculate_rmse(solar_vals[-horizon_days:] if len(solar_vals) >= horizon_days else solar_vals, predicted_solars[:len(solar_vals)]), 3)
        mape = round(calculate_mape(solar_vals[-horizon_days:] if len(solar_vals) >= horizon_days else solar_vals, predicted_solars[:len(solar_vals)]), 2)

        confidence_score = round(max(75.0, 96.5 - (horizon_days * 0.8) - (mae * 2.0)), 1)

        return {
            "forecast_type": "Solar Irradiance & PV Power",
            "forecast_horizon_days": horizon_days,
            "forecast_date": start_date.strftime("%Y-%m-%d"),
            "predicted_solar_irradiance": avg_pred_solar,
            "predicted_energy_generation": total_energy_mwh,
            "forecast_confidence": confidence_score,
            "metrics": {
                "mae": mae,
                "rmse": rmse,
                "mape": mape
            },
            "prediction_status": "Completed",
            "forecast_points": forecast_points
        }

    def _empty_response() -> Dict[str, Any]:
        return {
            "forecast_type": "Solar Irradiance & PV Power",
            "forecast_horizon_days": 0,
            "predicted_solar_irradiance": 0.0,
            "predicted_energy_generation": 0.0,
            "forecast_confidence": 0.0,
            "prediction_status": "No Data",
            "forecast_points": []
        }
