"""
Annual Revenue Estimation Module
"""

import logging
from app.services.financial.utils import validate_positive_value

logger = logging.getLogger("financial.revenue")


def estimate_annual_revenue(
    annual_energy_yield: float,
    electricity_tariff: float
) -> float:
    """
    Estimates Annual Revenue using formula:
    Revenue = Energy Yield * Tariff

    :param annual_energy_yield: Annual Energy Yield in kWh
    :param electricity_tariff: Tariff in currency / kWh (e.g., ₹/kWh or $/kWh)
    :return: Estimated Annual Revenue
    """
    yield_val = validate_positive_value(annual_energy_yield, "Annual energy yield")
    tariff_val = validate_positive_value(electricity_tariff, "Electricity tariff")

    revenue = yield_val * tariff_val
    revenue = round(revenue, 2)

    logger.info("Revenue Estimated: %s (Yield: %s kWh, Tariff: %s)", revenue, yield_val, tariff_val)
    return revenue
