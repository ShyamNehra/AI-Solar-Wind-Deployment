from typing import Dict, Any


class EnergyYieldService:
    """
    Dedicated engineering service for calculating realistic annual energy yields (MWh/year).
    Accounts for physical site parameters, installed capacity, capacity factor scaling,
    system efficiency, and operational degradation.
    """

    DEFAULT_SOLAR_CF = 0.20  # Baseline 20% capacity factor for solar PV
    DEFAULT_WIND_CF = 0.35   # Baseline 35% capacity factor for onshore wind
    DEFAULT_SYSTEM_EFFICIENCY = 0.85  # 85% system efficiency (15% base loss)
    HOURS_PER_YEAR = 8760.0

    def estimate_solar_yield(self, capacity_mw: float, env_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates expected annual solar energy yield (Tasks 2 & 3).
        Scales capacity factor dynamically based on irradiance (benchmark ~5.0 kWh/m²/day).
        """
        irradiance = float(env_features.get("solar_irradiance", 5.0))
        
        # Determine capacity factor (use user-specified value or scale dynamically via irradiance)
        if "capacity_factor" in env_features:
            applied_cf = float(env_features["capacity_factor"])
        else:
            applied_cf = min(0.30, max(0.10, (irradiance / 5.0) * self.DEFAULT_SOLAR_CF))

        efficiency = float(env_features.get("system_efficiency", self.DEFAULT_SYSTEM_EFFICIENCY))
        op_losses = float(env_features.get("operational_losses", 0.05))  # 5% soiling/thermal loss

        gross_yield_mwh = capacity_mw * self.HOURS_PER_YEAR * applied_cf
        net_yield_mwh = gross_yield_mwh * efficiency * (1.0 - op_losses)

        return {
            "technology": "solar",
            "installed_capacity_mw": capacity_mw,
            "applied_capacity_factor": round(applied_cf, 4),
            "system_efficiency": efficiency,
            "operational_loss_pct": round(op_losses * 100, 2),
            "annual_gross_yield_mwh": round(gross_yield_mwh, 2),
            "annual_net_yield_mwh": round(net_yield_mwh, 2)
        }

    def estimate_wind_yield(self, capacity_mw: float, env_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates expected annual wind energy yield (Tasks 2 & 3).
        Scales capacity factor non-linearly with wind speed relative to standard rated speed (10 m/s).
        """
        wind_speed = float(env_features.get("wind_speed", 8.0))

        if "capacity_factor" in env_features:
            applied_cf = float(env_features["capacity_factor"])
        else:
            applied_cf = min(0.50, max(0.12, ((wind_speed / 10.0) ** 3) * self.DEFAULT_WIND_CF))

        efficiency = float(env_features.get("system_efficiency", self.DEFAULT_SYSTEM_EFFICIENCY))
        op_losses = float(env_features.get("operational_losses", 0.04))  # 4% wake/curtailment loss

        gross_yield_mwh = capacity_mw * self.HOURS_PER_YEAR * applied_cf
        net_yield_mwh = gross_yield_mwh * efficiency * (1.0 - op_losses)

        return {
            "technology": "wind",
            "installed_capacity_mw": capacity_mw,
            "applied_capacity_factor": round(applied_cf, 4),
            "system_efficiency": efficiency,
            "operational_loss_pct": round(op_losses * 100, 2),
            "annual_gross_yield_mwh": round(gross_yield_mwh, 2),
            "annual_net_yield_mwh": round(net_yield_mwh, 2)
        }

    def estimate_hybrid_yield(self, capacity_mw: float, env_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates yield for a co-located Solar + Wind hybrid facility (Tasks 2 & 3).
        Allocates capacity 50/50 across technologies.
        """
        split_capacity = capacity_mw / 2.0
        solar_eval = self.estimate_solar_yield(split_capacity, env_features)
        wind_eval = self.estimate_wind_yield(split_capacity, env_features)

        total_gross = solar_eval["annual_gross_yield_mwh"] + wind_eval["annual_gross_yield_mwh"]
        total_net = solar_eval["annual_net_yield_mwh"] + wind_eval["annual_net_yield_mwh"]
        blended_cf = round((solar_eval["applied_capacity_factor"] + wind_eval["applied_capacity_factor"]) / 2.0, 4)

        return {
            "technology": "hybrid_solar_wind",
            "installed_capacity_mw": capacity_mw,
            "applied_capacity_factor": blended_cf,
            "solar_net_yield_mwh": solar_eval["annual_net_yield_mwh"],
            "wind_net_yield_mwh": wind_eval["annual_net_yield_mwh"],
            "annual_gross_yield_mwh": round(total_gross, 2),
            "annual_net_yield_mwh": round(total_net, 2)
        }

    def calculate_yield(self, deployment_type: str, env_features: Dict[str, Any]) -> Dict[str, Any]:
        """Main evaluation entry point for routing requests."""
        capacity_mw = float(env_features.get("installed_capacity_mw", 10.0))  # Default 10 MW standard site
        dtype = deployment_type.lower()

        if "solar" in dtype and "wind" in dtype:
            return self.estimate_hybrid_yield(capacity_mw, env_features)
        elif "wind" in dtype:
            return self.estimate_wind_yield(capacity_mw, env_features)
        else:
            return self.estimate_solar_yield(capacity_mw, env_features)