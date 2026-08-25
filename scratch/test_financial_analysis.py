import sys
import os

# Add root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.financial_analysis_service import FinancialAnalysisService
from app.services.analysis_pipeline import AnalysisPipelineService
from schemas.analysis import AnalysisRequest

# Mock Clients to bypass network connections during pipeline testing
class MockNASAPowerClient:
    def __init__(self, solar_irradiance: float = 5.4):
        self.solar_irradiance = solar_irradiance

    def get_solar_data(self, latitude: float, longitude: float) -> dict:
        return {
            "properties": {
                "parameter": {
                    "ALLSKY_SFC_SW_DWN": {"ANN": self.solar_irradiance},
                    "T2M": {"ANN": 28.5},
                    "RH2M": {"ANN": 62.0}
                }
            }
        }

class MockGlobalWindAtlasClient:
    def get_wind_data(self, latitude: float, longitude: float) -> dict:
        raise NotImplementedError("Use WindFeatureEngineer fallback mock data")

def test_financial_service_calculations():
    print("=== Testing Financial Service Calculations & Edge Cases ===")
    service = FinancialAnalysisService()

    # 1. Base Revenue calculation
    rev_base = service.estimate_annual_revenue(128450.0, 9.0)
    print(f"Base Revenue (Yield=128450, Tariff=9.0): {rev_base} INR")
    assert rev_base == 1156050.0

    # 2. Monotonicity: Increasing yield/tariff increases revenue
    rev_high_yield = service.estimate_annual_revenue(130000.0, 9.0)
    rev_high_tariff = service.estimate_annual_revenue(128450.0, 10.0)
    assert rev_high_yield > rev_base
    assert rev_high_tariff > rev_base

    # 3. Base Project Cost calculation
    cost_base = service.estimate_project_cost(
        installed_capacity_kw=2000.0,
        cost_per_kw=20000.0,
        additional_installation_percentage=10.0
    )
    print(f"Base Cost (Cap=2000kW, Cost=20000, Add=10%): {cost_base} INR")
    assert cost_base == 44000000.0

    # 4. Monotonicity: Increasing capacity/cost-per-kW/percentage increases project cost
    cost_high_cap = service.estimate_project_cost(25000.0, 20000.0, 10.0)
    cost_high_kw = service.estimate_project_cost(2000.0, 25000.0, 10.0)
    cost_high_pct = service.estimate_project_cost(2000.0, 20000.0, 15.0)
    assert cost_high_cap > cost_base
    assert cost_high_kw > cost_base
    assert cost_high_pct > cost_base

    # 5. Base Payback Period calculation
    payback_base = service.calculate_payback_period(
        total_project_cost=42000000.0,
        annual_revenue=11560000.0
    )
    print(f"Base Payback (Cost=42M, Rev=11.56M): {payback_base} Years")
    assert abs(payback_base - 3.63) < 0.01

    # 6. Monotonicity: Increasing project cost (revenue constant) increases payback period
    payback_high_cost = service.calculate_payback_period(45000000.0, 11560000.0)
    assert payback_high_cost > payback_base

    # 7. Monotonicity: Higher annual revenue (project cost constant) reduces payback period
    payback_high_rev = service.calculate_payback_period(42000000.0, 12000000.0)
    assert payback_high_rev < payback_base

    # 8. Base ROI calculation
    roi_base = service.calculate_roi(
        annual_revenue=11560000.0,
        total_project_cost=42000000.0
    )
    print(f"Base ROI (Rev=11.56M, Cost=42M): {roi_base}%")
    assert abs(roi_base - 27.52) < 0.01

    # 9. Monotonicity: Increasing project cost (revenue constant) changes ROI consistently (decreases ROI)
    roi_high_cost = service.calculate_roi(11560000.0, 45000000.0)
    assert roi_high_cost < roi_base

    # 10. Edge cases: Zero and negative revenue for payback
    payback_zero_rev = service.calculate_payback_period(42000000.0, 0.0)
    payback_neg_rev = service.calculate_payback_period(42000000.0, -1000.0)
    print(f"Edge case Payback (Zero Rev): {payback_zero_rev}, (Neg Rev): {payback_neg_rev}")
    assert payback_zero_rev == -1.0
    assert payback_neg_rev == -1.0

    # 11. Edge cases: Zero cost handling
    payback_zero_cost = service.calculate_payback_period(0.0, 11560000.0)
    roi_zero_cost = service.calculate_roi(11560000.0, 0.0)
    print(f"Edge case (Zero Cost) Payback: {payback_zero_cost}, ROI: {roi_zero_cost}%")
    assert payback_zero_cost == 0.0
    assert roi_zero_cost == -1.0

    # 12. Input validations (ValueErrors)
    try:
        service.estimate_annual_revenue(-1000.0, 9.0)
        assert False, "Should fail on negative yield"
    except ValueError:
        pass

    try:
        service.estimate_project_cost(-100.0, 20000.0)
        assert False, "Should fail on negative capacity"
    except ValueError:
        pass

    print("[OK] Financial service unit tests passed!\n")

def test_pipeline_financial_integration():
    print("=== Testing Pipeline Financial Integration ===")
    
    # Initialize pipeline with mocked clients
    pipeline = AnalysisPipelineService(
        nasa_client=MockNASAPowerClient(solar_irradiance=5.4),
        wind_client=MockGlobalWindAtlasClient()
    )

    request = AnalysisRequest(
        project_name="Odisha Coastal Hybrid Plant",
        location="Odisha Coast",
        latitude=19.8135,
        longitude=85.8312,
        elevation=15.0,
        slope=1.2,
        distance_to_road=0.5,
        distance_to_grid=3.5,
        installed_capacity_kw=1000.0,
        solar_system_efficiency=0.80,
        wind_operational_losses=0.15,
        electricity_tariff_inr_per_kwh=9.0,
        cost_per_kw=20000.0,
        additional_installation_percentage=10.0
    )

    # Run analysis
    res = pipeline.run_analysis(request)
    
    print("Consolidated Response Financial Keys:")
    print(f"  - annual_revenue: {res['annual_revenue']} INR")
    print(f"  - estimated_project_cost: {res['estimated_project_cost']} INR")
    print(f"  - payback_period: {res['payback_period']} Years")
    print(f"  - roi: {res['roi']}%")

    # Assert responses contain correct keys
    assert "annual_revenue" in res
    assert "estimated_project_cost" in res
    assert "payback_period" in res
    assert "roi" in res

    assert res["annual_revenue"] > 0
    assert res["estimated_project_cost"] == 22000000.0  # 1000 * 20000 * 1.10 = 22,000,000
    assert res["payback_period"] > 0
    assert res["roi"] > 0

    print("[OK] Pipeline financial integration tests passed!\n")

if __name__ == "__main__":
    test_financial_service_calculations()
    test_pipeline_financial_integration()
    print("All financial analysis verification tests completed successfully!")
