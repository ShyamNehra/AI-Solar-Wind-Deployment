"""
Return on Investment (ROI) Calculation Module
"""

import logging
from typing import Optional
from app.services.financial.utils import validate_positive_value, validate_strict_positive

logger = logging.getLogger("financial.roi")


def calculate_roi(
    annual_revenue: float,
    annual_cost: float,
    project_cost: float
) -> float:
    """
    Calculates ROI percentage (%) using formula:
    ROI % = ((Annual Revenue - Annual Cost) / Project Cost) * 100

    :param annual_revenue: Estimated Annual Revenue
    :param annual_cost: Estimated Annual Operating Cost (OPEX)
    :param project_cost: Total Project Capital Cost (CAPEX)
    :return: ROI Percentage (%)
    """
    rev = validate_positive_value(annual_revenue, "Annual revenue")
    cost_op = validate_positive_value(annual_cost, "Annual cost")
    cost_proj = validate_strict_positive(project_cost, "Project cost")

    net_annual_profit = rev - cost_op
    roi_pct = round((net_annual_profit / cost_proj) * 100.0, 2)

    logger.info("ROI Calculated: %s%% (Net Profit: %s, Project Cost: %s)", roi_pct, net_annual_profit, cost_proj)
    return roi_pct
