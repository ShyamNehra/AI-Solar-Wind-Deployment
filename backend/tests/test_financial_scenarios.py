# tests/test_financial_scenarios.py
from app.evaluation.financial_analysis_service import FinancialAnalysisService


def test_scenario_1_tariff_sensitivity():
    """Verify that increasing electricity tariff increases revenue & ROI while decreasing payback period."""
    service = FinancialAnalysisService()
    yield_mwh = 15000.0  # 15,000 MWh net annual yield

    # Base Tariff: ₹4.50 / kWh
    base_res = service.run_financial_analysis(
        deployment_type="solar",
        annual_energy_yield_mwh=yield_mwh,
        env_features={"installed_capacity_mw": 10.0, "electricity_tariff": 4.50}
    )

    # Premium Tariff: ₹6.00 / kWh
    premium_res = service.run_financial_analysis(
        deployment_type="solar",
        annual_energy_yield_mwh=yield_mwh,
        env_features={"installed_capacity_mw": 10.0, "electricity_tariff": 6.00}
    )

    assert premium_res["annual_revenue_inr"] > base_res["annual_revenue_inr"]
    assert premium_res["payback_period_years"] < base_res["payback_period_years"]
    assert premium_res["roi_percentage"] > base_res["roi_percentage"]

    print(f"\n✔ Base Tariff (₹4.50): Revenue ₹{base_res['annual_revenue_inr']:,} | Payback: {base_res['payback_period_years']} yrs | ROI: {base_res['roi_percentage']}%")
    print(f"✔ Premium Tariff (₹6.00): Revenue ₹{premium_res['annual_revenue_inr']:,} | Payback: {premium_res['payback_period_years']} yrs | ROI: {premium_res['roi_percentage']}%")


def test_scenario_2_edge_case_zero_revenue():
    """Verify system handles zero yield/revenue without division-by-zero crashes."""
    service = FinancialAnalysisService()

    zero_res = service.run_financial_analysis(
        deployment_type="solar",
        annual_energy_yield_mwh=0.0,
        env_features={"installed_capacity_mw": 10.0, "electricity_tariff": 4.50}
    )

    assert zero_res["annual_revenue_inr"] == 0.0
    assert zero_res["payback_period_years"] == 999.99
    assert zero_res["roi_percentage"] == -100.0
    print("\n✔ Zero Yield Edge Case Passed: Handled gracefully with infinite payback fallback.")


if __name__ == "__main__":
    test_scenario_1_tariff_sensitivity()
    test_scenario_2_edge_case_zero_revenue()