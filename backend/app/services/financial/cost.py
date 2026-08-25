"""
Project Cost Estimation Module
"""

import logging
from typing import Optional
from app.services.financial.utils import validate_positive_value

logger = logging.getLogger("financial.cost")


def estimate_project_cost(
    installed_capacity: float,
    cost_per_mw: float = 40000000.0,
    installation_pct: float = 0.10
) -> float:
    """
    Estimates Total Project Cost (CAPEX) using formula:
    Project Cost = Installed Capacity * Cost per MW + Additional Installation Cost

    :param installed_capacity: Installed Capacity in kW (or MW if < 50)
    :param cost_per_mw: Capital cost per MW (default: ₹40,000,000 / MW or $500,000 / MW)
    :param installation_pct: Additional installation cost as fraction of base cost (default: 0.10 / 10%)
    :return: Estimated Total Project Cost
    """
    cap = validate_positive_value(installed_capacity, "Installed capacity")
    cpm = validate_positive_value(cost_per_mw, "Cost per MW")
    inst_pct = validate_positive_value(installation_pct, "Installation percentage")

    # If installation_pct > 1.0 (e.g. 10%), convert to decimal fraction (0.10)
    if inst_pct > 1.0:
        inst_pct = inst_pct / 100.0

    # Convert installed capacity from kW to MW if capacity is specified in kW (>= 10.0)
    capacity_mw = cap / 1000.0 if cap >= 10.0 else cap

    base_cost = capacity_mw * cpm
    additional_installation_cost = base_cost * inst_pct
    total_project_cost = round(base_cost + additional_installation_cost, 2)

    logger.info(
        "Project Cost Estimated: %s (Capacity: %s kW, Cost/MW: %s, Additional Inst Cost: %s)",
        total_project_cost, cap, cpm, additional_installation_cost
    )
    return total_project_cost
