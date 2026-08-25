"""
Wind Speed and Turbine Power Generation Forecaster.
"""

from datetime import datetime, timedelta
import math
from typing import List, Dict, Any, Optional
from app.forecasting.utils import calculate_mae, calculate_rmse, calculate_mape, format_confidence_interval

class WindForecaster:
    """
    Forecasting model for multi-horizon Wind Speed (m/s)
    and expected Wind Turbine Energy Output (MWh/day).
    """

    def forecast(
        self,
        historical_records: List[Dict[str, Any]],
        horizon_days: int = 7,
        installed_capacity_mw: float = 50.0,
        hub_height_m: float = 100.0
    ) -> Dict[str, Any]:
        """
        Executes wind forecasting pipeline over a multi-day horizon.
        """
        if not historical_records:
            return self._empty_response()

        recent = historical_records[-14:] if len(historical_records) >= 14 else historical_records
        wind_vals = [r["wind_speed"] for r in recent]
        
        base_wind = sum(wind_vals) / len(wind_vals)
        alpha = 0.40

        smoothed_wind = wind_vals[0]
        for val in wind_vals[1:]:
            smoothed_wind = alpha * val + (1 - alpha) * smoothed_wind

        # Wind power law height extrapolation from 10m to hub height
        # v(h) = v_10 * (h / 10)^alpha_shear
        shear_exponent = 0.143
        hub_wind_factor = (hub_height_m / 10.0) ** shear_exponent

        last_date_str = historical_records[-1].get("date", datetime.now().strftime("%Y-%m-%d"))
        try:
            start_date = datetime.strptime(last_date_str, "%Y-%m-%d")
        except ValueError:
            start_date = datetime.now()

        forecast_points = []
        predicted_winds = []
        predicted_energies = []

        for i in range(1, horizon_days + 1):
            target_date = start_date + timedelta(days=i)
            day_of_year = target_date.timetuple().tm_yday

            seasonal_factor = 1.0 + 0.20 * math.cos(2 * math.pi * (day_of_year - 40) / 365)
            harmonic_drift = 0.35 * math.cos(i * 1.1)

            pred_wind_10m = max(0.8, round(smoothed_wind * seasonal_factor + harmonic_drift, 2))
            pred_wind_hub = round(pred_wind_10m * hub_wind_factor, 2)

            # Capacity factor calculation based on wind power curve
            # Betz limit & realistic turbine efficiency curve
            if pred_wind_hub < 3.0:
                cf = 0.0
            elif pred_wind_hub < 12.0:
                cf = min(0.48, 0.035 * ((pred_wind_hub - 3.0) ** 1.8))
            elif pred_wind_hub <= 25.0:
                cf = 0.45
            else:
                cf = 0.0  # Cut-out speed

            pred_energy_mwh = round(installed_capacity_mw * 24.0 * cf, 2)

            predicted_winds.append(pred_wind_10m)
            predicted_energies.append(pred_energy_mwh)

            ci = format_confidence_interval(pred_wind_10m, confidence_pct=95.0, error_std=0.06)

            forecast_points.append({
                "date": target_date.strftime("%Y-%m-%d"),
                "horizon_step": i,
                "predicted_wind_speed": pred_wind_10m,
                "predicted_hub_wind_speed": pred_wind_hub,
                "predicted_energy_generation": pred_energy_mwh,
                "capacity_factor": round(cf * 100, 1),
                "lower_bound": ci["lower_bound"],
                "upper_bound": ci["upper_bound"],
                "unit_speed": "m/s",
                "unit_energy": "MWh"
            })

        avg_pred_wind = round(sum(predicted_winds) / len(predicted_winds), 2)
        total_energy_mwh = round(sum(predicted_energies), 2)

        mae = round(calculate_mae(wind_vals[-horizon_days:] if len(wind_vals) >= horizon_days else wind_vals, predicted_winds[:len(wind_vals)]), 3)
        rmse = round(calculate_rmse(wind_vals[-horizon_days:] if len(wind_vals) >= horizon_days else wind_vals, predicted_winds[:len(wind_vals)]), 3)
        mape = round(calculate_mape(wind_vals[-horizon_days:] if len(wind_vals) >= horizon_days else wind_vals, predicted_winds[:len(wind_vals)]), 2)

        confidence_score = round(max(70.0, 94.0 - (horizon_days * 0.9) - (mae * 2.5)), 1)

        return {
            "forecast_type": "Wind Speed & Turbine Power",
            "forecast_horizon_days": horizon_days,
            "forecast_date": start_date.strftime("%Y-%m-%d"),
            "predicted_wind_speed": avg_pred_wind,
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
            "forecast_type": "Wind Speed & Turbine Power",
            "forecast_horizon_days": 0,
            "predicted_wind_speed": 0.0,
            "predicted_energy_generation": 0.0,
            "forecast_confidence": 0.0,
            "prediction_status": "No Data",
            "forecast_points": []
        }
