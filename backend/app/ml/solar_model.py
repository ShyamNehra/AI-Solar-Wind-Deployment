import os
import json

# Setup directory for artifacts
ML_ARTIFACTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "ml_artifacts"))
os.makedirs(ML_ARTIFACTS_DIR, exist_ok=True)

# Define physics-based parameters for Solar Potential Prediction Engine
SOLAR_PARAMETERS = {
    "panel_efficiency": 0.20,      # 20% standard monocrystalline panel efficiency
    "performance_ratio": 0.75,     # 75% standard NREL performance ratio (system losses)
    "reference_system_size_kwp": 1.0, # 1 kWp installed capacity reference size
    "panel_area_per_kwp_sqm": 5.0   # 5 sqm area required per 1 kWp capacity
}

# Save parameters to artifact file to satisfy artifact tracking constraint
SOLAR_ARTIFACT_PATH = os.path.join(ML_ARTIFACTS_DIR, "solar_parameters.json")
with open(SOLAR_ARTIFACT_PATH, "w") as f:
    json.dump(SOLAR_PARAMETERS, f, indent=4)

def predict_solar_potential(average_solar_irradiance: float) -> dict:
    """
    Calculate solar potential using physics-based NREL PV performance metrics.
    
    NOTE ON MACHINE LEARNING LIMITATION:
    A pure supervised XGBoost regressor is not implemented because true labeled historical 
    actual energy production target data is not yet available for these coordinates. 
    True ML training is flagged as a Phase 3+ enhancement.
    
    Formula:
    Annual Incident Irradiance (kWh/m^2/year) = daily_irradiance * 365.25
    Expected Annual Energy (kWh/year/kWp) = Annual Incident Irradiance * panel_efficiency * performance_ratio * panel_area_per_kwp_sqm
    Capacity Factor = Expected Annual Energy / (8766 hours * 1.0 kWp)
    """
    daily_irradiance = average_solar_irradiance
    annual_irradiance = round(daily_irradiance * 365.25, 2)
    peak_sun_hours = round(daily_irradiance, 2)
    
    # Calculate output per 1 kWp system
    eff = SOLAR_PARAMETERS["panel_efficiency"]
    pr = SOLAR_PARAMETERS["performance_ratio"]
    area = SOLAR_PARAMETERS["panel_area_per_kwp_sqm"]
    
    # Expected output in kWh/year per 1 kWp
    expected_energy_output = round(annual_irradiance * eff * pr * area, 2)
    
    # Capacity factor (fraction of annual peak output)
    capacity_factor = round(expected_energy_output / (8766.0 * 1.0), 4)
    
    return {
        "annual_irradiance": annual_irradiance,
        "peak_sun_hours": peak_sun_hours,
        "expected_energy_output": expected_energy_output,
        "capacity_factor": capacity_factor,
        "performance_ratio": pr,
        "model_type": "Physics-Based PV Performance Pipeline (NREL Standard)",
        "ml_version": "1.0.0-phase2-fallback"
    }
