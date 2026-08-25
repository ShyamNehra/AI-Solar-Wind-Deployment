"""
Solar Energy Estimation Module
"""

import logging
from typing import Optional
from app.services.energy.utils import (
    normalize_percentage,
    validate_capacity,
    validate_resource_value
)

logger = logging.getLogger("energy.solar")


def estimate_solar_energy(
    solar_irradiance: float,
    installed_capacity: float,
    capacity_factor: Optional[float] = None,
    system_efficiency: float = 0.85,
    operational_loss: float = 0.10
) -> float:
    """
    Estimates Annual Solar Energy Yield in kWh/year using engineering formula:
    Annual Energy (kWh) = Installed Capacity (kW) * 8760 * Capacity Factor * Efficiency * (1 - Operational Loss)

    :param solar_irradiance: Solar Irradiance (kWh/m2/day)
    :param installed_capacity: Installed Capacity (kW)
    :param capacity_factor: Capacity Factor (fraction 0-1 or percentage 0-100%). If None, computed from irradiance.
    :param system_efficiency: System Efficiency (fraction 0-1 or percentage)
    :param operational_loss: Operational Loss (fraction 0-1 or percentage)
    :return: Annual Solar Energy Yield in kWh/year
    """
    irr = validate_resource_value(solar_irradiance, "Solar Irradiance")
    cap = validate_capacity(installed_capacity)
    eff = normalize_percentage(system_efficiency, "System Efficiency")
    loss = normalize_percentage(operational_loss, "Operational Loss")

    if capacity_factor is not None:
        cf = normalize_percentage(capacity_factor, "Capacity Factor")
    else:
        # Estimate CF based on solar irradiance (typical STC rating at 1000 W/m2 or 6.0 kWh/m2/day standard)
        # CF ~ (Solar Irradiance / 24.0) * peak efficiency factor
        cf = min(0.40, max(0.05, (irr / 24.0) * 0.85))

    # Adjust CF if irradiance is lower/higher relative to baseline irradiance standard (e.g. 5.0 kWh/m2/day)
    # If explicit capacity_factor provided, adjust slightly by irradiance factor if irradiance provided
    if solar_irradiance > 0 and capacity_factor is not None:
        # Baseline reference irradiance ~ 5.0 kWh/m2/day
        irr_scaling = min(1.5, max(0.2, irr / 5.0))
        cf = min(0.50, cf * irr_scaling)

    annual_solar_yield = cap * 8760.0 * cf * eff * (1.0 - loss)
    annual_solar_yield = round(annual_solar_yield, 2)

    logger.info("Solar Yield Calculated: %s kWh/year (Capacity: %s kW, CF: %s, Irr: %s)", annual_solar_yield, cap, cf, irr)
    return annual_solar_yield
