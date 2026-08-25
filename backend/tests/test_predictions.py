import pytest
from app.ml.solar_model import predict_solar_potential
from app.ml.wind_model import predict_wind_potential

def test_solar_prediction_deterministic_given_fixed_input():
    """
    Test that the solar prediction engine returns identical results for a fixed input.
    """
    input_irradiance = 5.8358
    
    res1 = predict_solar_potential(input_irradiance)
    res2 = predict_solar_potential(input_irradiance)
    
    assert res1["annual_irradiance"] == res2["annual_irradiance"]
    assert res1["peak_sun_hours"] == res2["peak_sun_hours"]
    assert res1["expected_energy_output"] == res2["expected_energy_output"]
    assert res1["capacity_factor"] == res2["capacity_factor"]
    assert res1["performance_ratio"] == res2["performance_ratio"]
    
    # Confirm exact values check
    assert res1["annual_irradiance"] == round(5.8358 * 365.25, 2)
    assert res1["capacity_factor"] == round(res1["expected_energy_output"] / (8766.0 * 1.0), 4)

def test_wind_prediction_deterministic_given_fixed_input():
    """
    Test that the wind prediction engine returns identical results for a fixed input.
    """
    input_wind_speed = 2.67
    
    res1 = predict_wind_potential(input_wind_speed)
    res2 = predict_wind_potential(input_wind_speed)
    
    assert res1["average_wind_speed"] == res2["average_wind_speed"]
    assert res1["wind_power_density"] == res2["wind_power_density"]
    assert res1["turbulence_intensity"] == res2["turbulence_intensity"]
    assert res1["capacity_factor"] == res2["capacity_factor"]
    assert res1["expected_annual_energy_production"] == res2["expected_annual_energy_production"]
    
    # Confirm exact physics formulas
    expected_wpd = round(0.5 * 1.225 * (2.67 ** 3), 2)
    assert res1["wind_power_density"] == expected_wpd
    
    import math
    v = 2.67
    prob_operational = math.exp(-math.pi / 4 * (3.0 / v) ** 2) - math.exp(-math.pi / 4 * (25.0 / v) ** 2)
    expected_cf = round(max(0.0, min(0.50, 0.45 * prob_operational)), 4)
    assert res1["capacity_factor"] == expected_cf
