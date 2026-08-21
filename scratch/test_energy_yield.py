import sys
import os

# Add root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.energy_yield_service import EnergyYieldService
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

def test_energy_yield_scenarios():
    print("=== Running Energy Yield Service Scenario Tests ===")
    service = EnergyYieldService()

    # 1. Base solar yield
    solar_yield_base = service.estimate_solar_energy_yield(
        solar_irradiance=5.0,
        installed_capacity_kw=1000.0,
        system_efficiency=0.80
    )
    print(f"Base Solar Yield (I=5.0, Cap=1000kW, Eff=80%): {solar_yield_base} kWh")
    assert solar_yield_base > 0

    # 2. Solar Irradiance Monotonicity: Increasing solar irradiance increases yield
    solar_yield_high_irr = service.estimate_solar_energy_yield(
        solar_irradiance=6.0,
        installed_capacity_kw=1000.0,
        system_efficiency=0.80
    )
    print(f"High Solar Irradiance Yield (I=6.0): {solar_yield_high_irr} kWh")
    assert solar_yield_high_irr > solar_yield_base

    # 3. Efficiency Monotonicity: Increasing solar system efficiency increases yield
    solar_yield_high_eff = service.estimate_solar_energy_yield(
        solar_irradiance=5.0,
        installed_capacity_kw=1000.0,
        system_efficiency=0.90
    )
    print(f"High Efficiency Solar Yield (Eff=90%): {solar_yield_high_eff} kWh")
    assert solar_yield_high_eff > solar_yield_base

    # 4. Capacity Factor Monotonicity (Solar): Increasing solar capacity factor increases yield
    solar_yield_cf_base = service.estimate_solar_energy_yield(
        solar_irradiance=5.0,
        installed_capacity_kw=1000.0,
        system_efficiency=0.80,
        solar_capacity_factor=0.20
    )
    solar_yield_cf_high = service.estimate_solar_energy_yield(
        solar_irradiance=5.0,
        installed_capacity_kw=1000.0,
        system_efficiency=0.80,
        solar_capacity_factor=0.25
    )
    print(f"Solar CF Yield (CF=20%): {solar_yield_cf_base} kWh, (CF=25%): {solar_yield_cf_high} kWh")
    assert solar_yield_cf_high > solar_yield_cf_base

    # 5. Base wind yield
    wind_yield_base = service.estimate_wind_energy_yield(
        wind_speed=6.0,
        installed_capacity_kw=1000.0,
        losses=0.15
    )
    print(f"Base Wind Yield (WS=6.0, Cap=1000kW, Losses=15%): {wind_yield_base} kWh")
    assert wind_yield_base > 0

    # 6. Wind Speed Monotonicity: Increasing wind speed increases yield
    wind_yield_high_ws = service.estimate_wind_energy_yield(
        wind_speed=8.0,
        installed_capacity_kw=1000.0,
        losses=0.15
    )
    print(f"High Wind Speed Yield (WS=8.0): {wind_yield_high_ws} kWh")
    assert wind_yield_high_ws > wind_yield_base

    # 7. Capacity Factor Monotonicity (Wind): Increasing wind capacity factor override increases yield
    wind_yield_cf_base = service.estimate_wind_energy_yield(
        wind_speed=6.0,
        installed_capacity_kw=1000.0,
        wind_capacity_factor=0.30,
        losses=0.15
    )
    wind_yield_cf_high = service.estimate_wind_energy_yield(
        wind_speed=6.0,
        installed_capacity_kw=1000.0,
        wind_capacity_factor=0.35,
        losses=0.15
    )
    print(f"Wind CF Yield (CF=30%): {wind_yield_cf_base} kWh, (CF=35%): {wind_yield_cf_high} kWh")
    assert wind_yield_cf_high > wind_yield_cf_base

    # 8. Installed Capacity Monotonicity: Increasing capacity increases both solar and wind yields
    solar_yield_high_cap = service.estimate_solar_energy_yield(
        solar_irradiance=5.0,
        installed_capacity_kw=1500.0,
        system_efficiency=0.80
    )
    wind_yield_high_cap = service.estimate_wind_energy_yield(
        wind_speed=6.0,
        installed_capacity_kw=1500.0,
        losses=0.15
    )
    print(f"High Capacity Solar Yield (Cap=1500kW): {solar_yield_high_cap} kWh")
    print(f"High Capacity Wind Yield (Cap=1500kW): {wind_yield_high_cap} kWh")
    assert solar_yield_high_cap > solar_yield_base
    assert wind_yield_high_cap > wind_yield_base

    # 9. Operational-loss behavior: Increasing wind operational losses decreases wind yield
    wind_yield_more_loss = service.estimate_wind_energy_yield(
        wind_speed=6.0,
        installed_capacity_kw=1000.0,
        losses=0.20
    )
    print(f"Wind Yield with Higher Losses (Losses=20%): {wind_yield_more_loss} kWh")
    assert wind_yield_more_loss < wind_yield_base

    # 10. Hybrid Yield: Sum of split capacities is calculated correctly using integration factor
    hybrid_yield = service.estimate_hybrid_energy_yield(
        solar_yield=solar_yield_base,
        wind_yield=wind_yield_base,
        hybrid_efficiency=0.95
    )
    print(f"Hybrid Yield (Solar={solar_yield_base}, Wind={wind_yield_base}, Eff=95%): {hybrid_yield} kWh")
    expected_hybrid = (solar_yield_base + wind_yield_base) * 0.5 * 0.95
    assert abs(hybrid_yield - expected_hybrid) < 0.1

    print("[OK] Energy yield service function scenarios and monotonicity checks passed!\n")

def test_pipeline_yield_integration():
    print("=== Running Pipeline Yield Integration Tests ===")
    
    # 1. Solar dominant site (High Irradiance, low wind)
    pipeline_solar = AnalysisPipelineService(
        nasa_client=MockNASAPowerClient(solar_irradiance=7.0),
        wind_client=MockGlobalWindAtlasClient()
    )
    
    req_solar = AnalysisRequest(
        project_name="Solar Facility",
        location="High Sun Area",
        latitude=20.0,
        longitude=70.0,
        installed_capacity_kw=1000.0,
        solar_system_efficiency=0.80,
        wind_operational_losses=0.15
    )

    res_solar = pipeline_solar.run_analysis(req_solar)
    print(f"Solar dominant recommendation: {res_solar['deployment_recommendation']['deployment']}")
    print(f"  Solar annual yield: {res_solar['solar_energy_yield_kwh']} kWh")
    print(f"  Recommended Tech Yield: {res_solar['recommended_annual_energy_kwh']} kWh")
    assert res_solar["solar_energy_yield_kwh"] > 0
    assert res_solar["recommended_annual_energy_kwh"] == res_solar["solar_energy_yield_kwh"]

    # 2. Pipeline output structure checks
    required_keys = [
        "solar_energy_yield_kwh",
        "wind_energy_yield_kwh",
        "hybrid_energy_yield_kwh",
        "recommended_annual_energy_kwh"
    ]
    for key in required_keys:
        assert key in res_solar, f"Response missing yield output key: {key}"

    print("[OK] Pipeline yield integration checks passed!\n")

if __name__ == "__main__":
    test_energy_yield_scenarios()
    test_pipeline_yield_integration()
    print("All energy yield verification tests executed and passed successfully!")
