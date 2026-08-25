"""
Hybrid Energy Estimation Module
"""

import logging

logger = logging.getLogger("energy.hybrid")


def estimate_hybrid_energy(solar_yield: float, wind_yield: float) -> float:
    """
    Estimates Hybrid Annual Energy Yield by combining Solar Yield and Wind Yield.

    :param solar_yield: Annual Solar Energy Yield (kWh/year)
    :param wind_yield: Annual Wind Energy Yield (kWh/year)
    :return: Hybrid Annual Energy Yield (kWh/year)
    """
    sol = max(0.0, float(solar_yield or 0.0))
    wnd = max(0.0, float(wind_yield or 0.0))
    hybrid_yield = round(sol + wnd, 2)

    logger.info("Hybrid Yield Calculated: %s kWh/year (Solar: %s, Wind: %s)", hybrid_yield, sol, wnd)
    return hybrid_yield
