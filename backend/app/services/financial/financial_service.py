"""
Financial Analysis Service

Unified service orchestrating Revenue, Cost, Payback Period, and ROI calculations.
Independent of Machine Learning prediction.
"""

import logging
from typing import Dict, Any, Optional

from app.services.financial.revenue import estimate_annual_revenue
from app.services.financial.cost import estimate_project_cost
from app.services.financial.payback import calculate_payback_period
from app.services.financial.roi import calculate_roi

logger = logging.getLogger("services.financial")


class FinancialAnalysisService:
    """
    Independent service for performing financial evaluations of energy deployments.
    """

    def analyze_financials(
        self,
        annual_energy_yield: float,
        installed_capacity: float = 1000.0,
        electricity_tariff: float = 90.0,  # ₹/kWh (or tariff rate)
        cost_per_mw: float = 40000000.0,    # ₹40,000,000 / MW
        installation_pct: float = 0.10,     # 10%
        annual_opex_pct: float = 0.02       # 2% of CAPEX as annual OPEX
    ) -> Dict[str, Any]:
        """
        Executes financial analysis and returns revenue, project cost, payback period, and ROI.
        """
        logger.info("Financial Analysis Started (Yield: %s kWh, Capacity: %s kW)", annual_energy_yield, installed_capacity)

        # 1. Revenue Estimation
        annual_revenue = estimate_annual_revenue(
            annual_energy_yield=annual_energy_yield,
            electricity_tariff=electricity_tariff
        )
        logger.info("Revenue Estimated: %s", annual_revenue)

        # 2. Project Cost Estimation (CAPEX)
        project_cost = estimate_project_cost(
            installed_capacity=installed_capacity,
            cost_per_mw=cost_per_mw,
            installation_pct=installation_pct
        )
        logger.info("Project Cost Estimated: %s", project_cost)

        # 3. Annual Operating Cost (OPEX)
        annual_cost = round(project_cost * annual_opex_pct, 2)

        # 4. Payback Period Calculation
        try:
            payback_period = calculate_payback_period(
                project_cost=project_cost,
                annual_revenue=annual_revenue
            )
        except ValueError as e:
            logger.warning("Payback calculation notice: %s", e)
            payback_period = 0.0

        # 5. ROI Calculation
        roi = calculate_roi(
            annual_revenue=annual_revenue,
            annual_cost=annual_cost,
            project_cost=project_cost
        )
        logger.info("ROI Calculated: %s%%", roi)

        return {
            "annual_revenue": annual_revenue,
            "estimated_project_cost": project_cost,
            "annual_cost": annual_cost,
            "payback_period": payback_period,
            "roi": roi,
            "electricity_tariff": electricity_tariff
        }
