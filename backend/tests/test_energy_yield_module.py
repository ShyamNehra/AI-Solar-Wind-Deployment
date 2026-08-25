"""
Automated Tests for Energy Yield Estimation Module (Task 5 & Task 16)
"""

import pytest
from app.services.energy.solar_energy import estimate_solar_energy
from app.services.energy.wind_energy import estimate_wind_energy
from app.services.energy.hybrid_energy import estimate_hybrid_energy
from app.services.energy.energy_service import EnergyYieldService


def test_solar_energy_estimation():
    """Verify estimate_solar_energy produces realistic values."""
    # Capacity 1000 kW, CF 20%, Eff 85%, Loss 10%
    solar_yield = estimate_solar_energy(
        solar_irradiance=5.5,
        installed_capacity=1000.0,
        capacity_factor=0.20,
        system_efficiency=0.85,
        operational_loss=0.10
    )
    assert solar_yield > 0
    assert isinstance(solar_yield, float)


def test_wind_energy_estimation():
    """Verify estimate_wind_energy produces realistic values."""
    wind_yield = estimate_wind_energy(
        wind_speed=7.0,
        installed_capacity=1000.0,
        capacity_factor=0.35,
        system_efficiency=0.90,
        operational_loss=0.12
    )
    assert wind_yield > 0
    assert isinstance(wind_yield, float)


def test_hybrid_energy_estimation():
    """Verify estimate_hybrid_energy combines solar and wind yields."""
    sol = 1500000.0
    wnd = 2500000.0
    hybrid = estimate_hybrid_energy(sol, wnd)
    assert hybrid == 4000000.0


# ── Task 5 Test Scenarios ───────────────────────────────────────────────────

def test_scenario_1_high_solar_low_wind():
    """Scenario 1: High Solar, Low Wind -> Solar dominates."""
    service = EnergyYieldService()
    res = service.calculate_energy_yield(
        solar_irradiance=7.5,
        wind_speed=2.0,
        installed_capacity=1000.0,
        solar_capacity_factor=0.25,
        wind_capacity_factor=0.05
    )
    assert res["solar_energy_yield"] > res["wind_energy_yield"]


def test_scenario_2_high_wind_low_solar():
    """Scenario 2: High Wind, Low Solar -> Wind dominates."""
    service = EnergyYieldService()
    res = service.calculate_energy_yield(
        solar_irradiance=2.0,
        wind_speed=11.0,
        installed_capacity=1000.0,
        solar_capacity_factor=0.10,
        wind_capacity_factor=0.45
    )
    assert res["wind_energy_yield"] > res["solar_energy_yield"]


def test_scenario_3_both_high():
    """Scenario 3: Both High -> Hybrid highest."""
    service = EnergyYieldService()
    res = service.calculate_energy_yield(
        solar_irradiance=7.0,
        wind_speed=10.0,
        installed_capacity=1000.0,
        solar_capacity_factor=0.25,
        wind_capacity_factor=0.40
    )
    assert res["hybrid_energy_yield"] > res["solar_energy_yield"]
    assert res["hybrid_energy_yield"] > res["wind_energy_yield"]
    assert res["hybrid_energy_yield"] == res["solar_energy_yield"] + res["wind_energy_yield"]


def test_scenario_4_low_capacity_factor():
    """Scenario 4: Low Capacity Factor -> Reduced Energy."""
    service = EnergyYieldService()
    high_cf_res = service.calculate_energy_yield(
        solar_irradiance=5.5,
        wind_speed=6.5,
        installed_capacity=1000.0,
        solar_capacity_factor=0.25,
        wind_capacity_factor=0.35
    )
    low_cf_res = service.calculate_energy_yield(
        solar_irradiance=5.5,
        wind_speed=6.5,
        installed_capacity=1000.0,
        solar_capacity_factor=0.05,
        wind_capacity_factor=0.08
    )
    assert low_cf_res["annual_energy_yield"] < high_cf_res["annual_energy_yield"]


def test_scenario_5_high_operational_loss():
    """Scenario 5: High Operational Loss -> Lower Yield."""
    normal_loss_solar = estimate_solar_energy(
        solar_irradiance=5.5,
        installed_capacity=1000.0,
        capacity_factor=0.20,
        operational_loss=0.10
    )
    high_loss_solar = estimate_solar_energy(
        solar_irradiance=5.5,
        installed_capacity=1000.0,
        capacity_factor=0.20,
        operational_loss=0.35
    )
    assert high_loss_solar < normal_loss_solar


def test_energy_yield_validation_errors():
    """Verify input validation handles invalid inputs."""
    with pytest.raises(ValueError):
        estimate_solar_energy(solar_irradiance=-1.0, installed_capacity=1000.0)

    with pytest.raises(ValueError):
        estimate_solar_energy(solar_irradiance=5.0, installed_capacity=-500.0)

    with pytest.raises(ValueError):
        estimate_solar_energy(solar_irradiance=5.0, installed_capacity=1000.0, capacity_factor=150.0)
