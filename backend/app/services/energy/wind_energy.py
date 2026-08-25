"""
Wind Energy Estimation Module
"""

import logging
from typing import Optional
from app.services.energy.utils import (
    normalize_percentage,
    validate_capacity,
    validate_resource_value
)

logger = logging.getLogger("energy.wind")


def estimate_wind_energy(
    wind_speed: float,
    installed_capacity: float,
    capacity_factor: Optional[float] = None,
    system_efficiency: float = 0.90,
    operational_loss: float = 0.12
) -> float:
    """
    Estimates Annual Wind Energy Yield in kWh/year using engineering formula:
    Annual Energy (kWh) = Installed Capacity (kW) * 8760 * Capacity Factor * Efficiency * (1 - Operational Loss)

    :param wind_speed: Wind Speed (m/s)
    :param installed_capacity: Installed Capacity (kW)
    :param capacity_factor: Capacity Factor (fraction 0-1 or percentage 0-100%). If None, computed from wind speed.
    :param system_efficiency: System Efficiency (fraction 0-1 or percentage)
    :param operational_loss: Operational Loss (fraction 0-1 or percentage)
    :return: Annual Wind Energy Yield in kWh/year
    """
    ws = validate_resource_value(wind_speed, "Wind Speed")
    cap = validate_capacity(installed_capacity)
    eff = normalize_percentage(system_efficiency, "System Efficiency")
    loss = normalize_percentage(operational_loss, "Operational Loss")

    if capacity_factor is not None:
        cf = normalize_percentage(capacity_factor, "Capacity Factor")
    else:
        # Rayleigh / Betz approximation for CF based on average wind speed (m/s)
        # Cut-in ~3 m/s, rated ~12 m/s
        if ws < 3.0:
            cf = 0.0
        elif ws >= 12.0:
            cf = 0.48
        else:
            cf = 0.05 + ((ws - 3.0) / 9.0) * 0.40

    # Adjust CF using wind speed relative to baseline rated speed (~7.0 m/s) if wind speed is provided
    if ws > 0 and capacity_factor is not None:
        if ws < 3.0:
            cf = 0.0
        else:
            speed_scaling = min(1.5, max(0.1, (ws / 7.0) ** 2))
            cf = min(0.60, cf * speed_scaling)

    annual_wind_yield = cap * 8760.0 * cf * eff * (1.0 - loss)
    annual_wind_yield = round(annual_wind_yield, 2)

    logger.info("Wind Yield Calculated: %s kWh/year (Capacity: %s kW, CF: %s, Speed: %s)", annual_wind_yield, cap, cf, ws)
    return annual_wind_yield
