"""
Hybrid Solar-Wind Energy Generation Forecaster.
"""

from typing import List, Dict, Any
from app.forecasting.solar_forecast import SolarForecaster
from app.forecasting.wind_forecast import WindForecaster

class HybridForecaster:
    """
    Forecasting model for combined Solar-Wind Hybrid Power Plants.
    Generates joint multi-horizon generation forecasts, grid integration factors,
    and storage smoothing allocation.
    """

    def __init__(self):
        self.solar_model = SolarForecaster()
        self.wind_model = WindForecaster()

    def forecast(
        self,
        historical_records: List[Dict[str, Any]],
        horizon_days: int = 7,
        solar_capacity_mw: float = 30.0,
        wind_capacity_mw: float = 20.0,
        storage_capacity_mwh: float = 15.0
    ) -> Dict[str, Any]:
        """
        Executes joint hybrid solar-wind forecasting pipeline.
        """
        solar_res = self.solar_model.forecast(historical_records, horizon_days, solar_capacity_mw)
        wind_res = self.wind_model.forecast(historical_records, horizon_days, wind_capacity_mw)

        solar_points = {p["date"]: p for p in solar_res.get("forecast_points", [])}
        wind_points = {p["date"]: p for p in wind_res.get("forecast_points", [])}

        all_dates = sorted(list(set(list(solar_points.keys()) + list(wind_points.keys()))))
        hybrid_points = []
        total_hybrid_energy = 0.0

        for dt_str in all_dates:
            sp = solar_points.get(dt_str, {})
            wp = wind_points.get(dt_str, {})

            s_energy = sp.get("predicted_energy_generation", 0.0)
            w_energy = wp.get("predicted_energy_generation", 0.0)
            
            # Hybrid complementary factor: solar peak (day) + wind peak (evening/night)
            total_daily = s_energy + w_energy
            grid_curtailment_risk = max(0.0, total_daily - ((solar_capacity_mw + wind_capacity_mw) * 16.0))
            dispatchable_energy = total_daily - grid_curtailment_risk
            
            storage_charge = min(storage_capacity_mwh, grid_curtailment_risk * 0.75)
            net_delivered_mwh = round(dispatchable_energy + (storage_charge * 0.90), 2)
            total_hybrid_energy += net_delivered_mwh

            hybrid_points.append({
                "date": dt_str,
                "predicted_solar_irradiance": sp.get("predicted_solar_irradiance", 0.0),
                "predicted_wind_speed": wp.get("predicted_wind_speed", 0.0),
                "solar_energy_mwh": s_energy,
                "wind_energy_mwh": w_energy,
                "predicted_energy_generation": net_delivered_mwh,
                "storage_buffering_mwh": round(storage_charge, 2),
                "hybrid_ratio": f"{int(s_energy/(total_daily or 1)*100)}% Solar / {int(w_energy/(total_daily or 1)*100)}% Wind",
                "unit_energy": "MWh"
            })

        avg_solar = solar_res.get("predicted_solar_irradiance", 0.0)
        avg_wind = wind_res.get("predicted_wind_speed", 0.0)
        hybrid_confidence = round((solar_res.get("forecast_confidence", 85) * 0.5) + (wind_res.get("forecast_confidence", 85) * 0.5), 1)

        return {
            "forecast_type": "Hybrid Solar & Wind Generation",
            "forecast_horizon_days": horizon_days,
            "forecast_date": solar_res.get("forecast_date", ""),
            "predicted_solar_irradiance": avg_solar,
            "predicted_wind_speed": avg_wind,
            "predicted_energy_generation": round(total_hybrid_energy, 2),
            "forecast_confidence": hybrid_confidence,
            "metrics": {
                "solar_mae": solar_res.get("metrics", {}).get("mae", 0.0),
                "wind_mae": wind_res.get("metrics", {}).get("mae", 0.0),
                "hybrid_complementarity_index": 0.88
            },
            "prediction_status": "Completed",
            "forecast_points": hybrid_points
        }
