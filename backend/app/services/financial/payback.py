"""
Payback Period Calculation Module
"""

import logging
from app.services.financial.utils import validate_positive_value

logger = logging.getLogger("financial.payback")


def calculate_payback_period(
    project_cost: float,
    annual_revenue: float
) -> float:
    """
    Calculates Payback Period in years using formula:
    Payback Period = Project Cost / Annual Revenue

    :param project_cost: Total Project Cost (CAPEX)
    :param annual_revenue: Estimated Annual Revenue
    :return: Payback Period in years
    """
    cost = validate_positive_value(project_cost, "Project cost")
    
    if annual_revenue is None:
        raise ValueError("Annual revenue cannot be None")
    
    rev = float(annual_revenue)
    if rev <= 0:
        raise ValueError("Annual revenue must be strictly positive (> 0) to calculate a valid payback period")

    payback_years = round(cost / rev, 2)
    logger.info("Payback Period Calculated: %s years (Cost: %s, Revenue: %s)", payback_years, cost, rev)
    return payback_years
