"""
Energy Estimation Service

Provides annual energy yield calculations for solar, wind, and hybrid deployments.
Reused across forecasting, capacity planning, pipeline workflow, and API endpoints.
"""

from typing import Dict, Optional, Any, Union


def calculate_solar_energy(
    installed_capacity: float,
    solar_capacity_factor: float,
    operating_hours: float = 8760.0
) -> float:
    """
    Calculates expected annual solar energy production in kWh.
    """
    cap = float(installed_capacity)
    if cap < 0:
        raise ValueError("Installed capacity cannot be negative")

    hours = float(operating_hours)
    if hours < 0:
        raise ValueError("Operating hours cannot be negative")

    cf = float(solar_capacity_factor)
    if cf < 0:
        raise ValueError("Capacity factor cannot be negative")
    if cf > 100.0:
        raise ValueError("Capacity factor cannot exceed 100%")

    cf_fraction = cf if cf <= 1.0 else cf / 100.0
    return round(cap * cf_fraction * hours, 2)


def calculate_wind_energy(
    installed_capacity: float,
    wind_capacity_factor: float,
    operating_hours: float = 8760.0
) -> float:
    """
    Calculates expected annual wind energy production in kWh.
    """
    cap = float(installed_capacity)
    if cap < 0:
        raise ValueError("Installed capacity cannot be negative")

    hours = float(operating_hours)
    if hours < 0:
        raise ValueError("Operating hours cannot be negative")

    cf = float(wind_capacity_factor)
    if cf < 0:
        raise ValueError("Capacity factor cannot be negative")
    if cf > 100.0:
        raise ValueError("Capacity factor cannot exceed 100%")

    cf_fraction = cf if cf <= 1.0 else cf / 100.0
    return round(cap * cf_fraction * hours, 2)


class EnergyEstimationService:
    """
    Service layer to calculate energy estimates for candidate sites and deployment parameters.
    """

    def estimate_energy(
        self,
        site_evaluation_result: Optional[Dict[str, Any]] = None,
        deployment_type: str = "Hybrid",
        installed_capacity: float = 1000.0,
        operating_hours: float = 8760.0,
        solar_capacity_factor: Optional[float] = None,
        wind_capacity_factor: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Estimates energy yield based on deployment type and capacity factors.
        """
        cap = float(installed_capacity)
        if cap < 0:
            raise ValueError("Installed capacity cannot be negative")

        hours = float(operating_hours)
        if hours < 0:
            raise ValueError("Operating hours cannot be negative")

        dep_type = (deployment_type or "Hybrid").capitalize()

        # Extract CF from site_evaluation_result if not explicitly supplied
        sol_cf = solar_capacity_factor
        wnd_cf = wind_capacity_factor

        if site_evaluation_result and isinstance(site_evaluation_result, dict):
            if sol_cf is None:
                sol_cf = site_evaluation_result.get("solar_assessment", {}).get("capacity_factor")
            if wnd_cf is None:
                wnd_cf = site_evaluation_result.get("wind_assessment", {}).get("capacity_factor")

        sol_cf = sol_cf if sol_cf is not None else 20.0
        wnd_cf = wnd_cf if wnd_cf is not None else 35.0

        if dep_type == "Solar":
            solar_energy = calculate_solar_energy(cap, sol_cf, hours)
            wind_energy = 0.0
            cf_used = sol_cf
        elif dep_type == "Wind":
            solar_energy = 0.0
            wind_energy = calculate_wind_energy(cap, wnd_cf, hours)
            cf_used = wnd_cf
        else: # Hybrid
            solar_energy = calculate_solar_energy(cap, sol_cf, hours)
            wind_energy = calculate_wind_energy(cap, wnd_cf, hours)
            cf_used = {"solar": sol_cf, "wind": wnd_cf}

        total_energy = round(solar_energy + wind_energy, 2)

        return {
            "solar_energy": solar_energy,
            "wind_energy": wind_energy,
            "total_energy": total_energy,
            "deployment_type": dep_type,
            "installed_capacity": cap,
            "capacity_factor_used": cf_used,
            "operating_hours": hours
        }
