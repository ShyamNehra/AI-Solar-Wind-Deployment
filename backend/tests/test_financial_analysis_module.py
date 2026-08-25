"""
Automated Tests for Financial Analysis Module (Task 6 - 9 & Task 15, 16)
"""

import pytest
from app.services.financial.revenue import estimate_annual_revenue
from app.services.financial.cost import estimate_project_cost
from app.services.financial.payback import calculate_payback_period
from app.services.financial.roi import calculate_roi
from app.services.financial.financial_service import FinancialAnalysisService


def test_annual_revenue_calculation():
    """Verify Revenue = Energy Yield * Tariff."""
    revenue = estimate_annual_revenue(annual_energy_yield=100000.0, electricity_tariff=90.0)
    assert revenue == 9000000.0


def test_project_cost_calculation():
    """Verify Project Cost = Capacity * Cost per MW + Additional Installation Cost."""
    # Installed capacity 1000 kW (1 MW), Cost per MW 40,000,000, Installation 10%
    cost = estimate_project_cost(installed_capacity=1000.0, cost_per_mw=40000000.0, installation_pct=0.10)
    assert cost == 44000000.0


def test_payback_period_calculation():
    """Verify Payback Period = Project Cost / Annual Revenue."""
    payback = calculate_payback_period(project_cost=40000000.0, annual_revenue=10000000.0)
    assert payback == 4.0


def test_roi_calculation():
    """Verify ROI = ((Annual Revenue - Annual Cost) / Project Cost) * 100."""
    roi = calculate_roi(annual_revenue=12000000.0, annual_cost=2000000.0, project_cost=40000000.0)
    assert roi == 25.0


def test_financial_service_integration():
    """Verify FinancialAnalysisService returns all required fields."""
    service = FinancialAnalysisService()
    res = service.analyze_financials(
        annual_energy_yield=1284500.0,
        installed_capacity=1000.0,
        electricity_tariff=90.0
    )
    assert "annual_revenue" in res
    assert "estimated_project_cost" in res
    assert "payback_period" in res
    assert "roi" in res
    assert res["annual_revenue"] > 0
    assert res["estimated_project_cost"] > 0
    assert res["payback_period"] > 0
    assert res["roi"] > 0


def test_financial_error_handling():
    """Verify robust error handling for zero/negative revenue, negative tariff, and negative capacity."""
    with pytest.raises(ValueError):
        estimate_annual_revenue(annual_energy_yield=1000.0, electricity_tariff=-5.0)

    with pytest.raises(ValueError):
        estimate_project_cost(installed_capacity=-100.0)

    with pytest.raises(ValueError):
        calculate_payback_period(project_cost=40000000.0, annual_revenue=0.0)

    with pytest.raises(ValueError):
        calculate_payback_period(project_cost=40000000.0, annual_revenue=-10000.0)
