import os
import json

# Setup directory for artifacts
ML_ARTIFACTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "ml_artifacts"))
os.makedirs(ML_ARTIFACTS_DIR, exist_ok=True)

import math

# Define physics-based parameters for Wind Potential Prediction Engine
WIND_PARAMETERS = {
    "air_density_kg_cum": 1.225,       # Sea-level standard air density (WMO standard)
    "reference_turbine_kw": 2000.0,    # 2 MW standard wind turbine
    "baseline_turbulence_intensity": 0.12, # 12% standard turbulence intensity baseline
    "cut_in_speed_mps": 3.0,           # Turbine cut-in wind speed
    "cut_out_speed_mps": 25.0,         # Turbine cut-out wind speed
    "power_curve_discount_factor": 0.45 # Standard efficiency discount factor including Betz limit and system losses
}

# Save parameters to artifact file to satisfy artifact tracking constraint
WIND_ARTIFACT_PATH = os.path.join(ML_ARTIFACTS_DIR, "wind_parameters.json")
with open(WIND_ARTIFACT_PATH, "w") as f:
    json.dump(WIND_PARAMETERS, f, indent=4)

def predict_wind_potential(average_wind_speed: float) -> dict:
    """
    Calculate wind potential using standard aerodynamic wind power density equations.
    
    NOTE ON MACHINE LEARNING LIMITATION:
    An LSTM or Prophet model is not trained because historical wind time-series production 
    data is not available for these coordinates. Physics/statistical equations are used as 
    a deviation, with true ML time-series training flagged as a Phase 3+ enhancement.
    
    Formula:
    Wind Power Density (WPD) = 0.5 * air_density * wind_speed^3
    Rayleigh CDF Operational Hours Probability:
      P(3.0 <= v_inst <= 25.0) = exp(-pi/4 * (3.0/v_mean)^2) - exp(-pi/4 * (25.0/v_mean)^2)
    Capacity Factor (Rayleigh-CDF discounted by conversion efficiency):
      CF = power_curve_discount_factor * P(3.0 <= v_inst <= 25.0)
    Expected Annual Energy (AEP, in kWh/year) = Rated Turbine Capacity * 8766 hours * Capacity Factor
    """
    v = average_wind_speed
    rho = WIND_PARAMETERS["air_density_kg_cum"]
    
    # Wind Power Density (W/m^2)
    wpd = round(0.5 * rho * (v ** 3), 2)
    
    # Bounded Rayleigh statistical approximation for Capacity Factor
    if v <= 0.1:
        capacity_factor = 0.0
    else:
        v_in = WIND_PARAMETERS["cut_in_speed_mps"]
        v_out = WIND_PARAMETERS["cut_out_speed_mps"]
        discount = WIND_PARAMETERS["power_curve_discount_factor"]
        prob_operational = math.exp(-math.pi / 4 * (v_in / v) ** 2) - math.exp(-math.pi / 4 * (v_out / v) ** 2)
        capacity_factor = round(max(0.0, min(0.50, discount * prob_operational)), 4)
    
    # Expected Annual Energy Production (AEP) in kWh/year for the 2MW reference turbine
    rated_kw = WIND_PARAMETERS["reference_turbine_kw"]
    aep = round(rated_kw * 8766.0 * capacity_factor, 2)
    
    return {
        "average_wind_speed": round(v, 2),
        "wind_power_density": wpd,
        "turbulence_intensity": WIND_PARAMETERS["baseline_turbulence_intensity"],
        "capacity_factor": capacity_factor,
        "expected_annual_energy_production": aep,
        "model_type": "Physics-Based Aerodynamic Performance Pipeline",
        "ml_version": "1.0.0-phase2-fallback"
    }
