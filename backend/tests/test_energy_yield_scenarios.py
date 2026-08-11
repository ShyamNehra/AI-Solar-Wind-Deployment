# tests/test_energy_yield_scenarios.py
from app.evaluation.energy_yield_service import EnergyYieldService


def test_scenario_1_solar_irradiance_scaling():
    """Validates that higher solar irradiance yields proportionally higher net energy."""
    service = EnergyYieldService()
    
    moderate_sun = service.calculate_yield("solar", {"installed_capacity_mw": 10.0, "solar_irradiance": 4.5})
    high_sun = service.calculate_yield("solar", {"installed_capacity_mw": 10.0, "solar_irradiance": 6.8})

    assert high_sun["annual_net_yield_mwh"] > moderate_sun["annual_net_yield_mwh"]
    assert high_sun["applied_capacity_factor"] > moderate_sun["applied_capacity_factor"]
    print(f"\n[Solar Scaling Pass] Moderate Sun: {moderate_sun['annual_net_yield_mwh']} MWh | High Sun: {high_sun['annual_net_yield_mwh']} MWh")


def test_scenario_2_wind_speed_and_loss_impact():
    """Validates wind generation behavior under varying wind speeds and operational degradation."""
    service = EnergyYieldService()

    base_wind = service.calculate_yield("wind", {"installed_capacity_mw": 15.0, "wind_speed": 7.5, "operational_losses": 0.04})
    high_loss_wind = service.calculate_yield("wind", {"installed_capacity_mw": 15.0, "wind_speed": 7.5, "operational_losses": 0.15})

    assert base_wind["annual_net_yield_mwh"] > high_loss_wind["annual_net_yield_mwh"]
    print(f"[Wind Loss Pass] 4% Loss Yield: {base_wind['annual_net_yield_mwh']} MWh | 15% Loss Yield: {high_loss_wind['annual_net_yield_mwh']} MWh")


def test_scenario_3_hybrid_co_location():
    """Validates hybrid facility yield generation aggregating solar and wind yields."""
    service = EnergyYieldService()

    hybrid_site = service.calculate_yield("hybrid_solar_wind", {
        "installed_capacity_mw": 20.0,
        "solar_irradiance": 5.5,
        "wind_speed": 8.5
    })

    assert hybrid_site["technology"] == "hybrid_solar_wind"
    assert hybrid_site["solar_net_yield_mwh"] > 0
    assert hybrid_site["wind_net_yield_mwh"] > 0
    assert hybrid_site["annual_net_yield_mwh"] == round(hybrid_site["solar_net_yield_mwh"] + hybrid_site["wind_net_yield_mwh"], 2)
    print(f"[Hybrid Pass] Total Net Hybrid Yield: {hybrid_site['annual_net_yield_mwh']} MWh")


if __name__ == "__main__":
    test_scenario_1_solar_irradiance_scaling()
    test_scenario_2_wind_speed_and_loss_impact()
    test_scenario_3_hybrid_co_location()