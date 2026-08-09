# Energy Yield Estimation Module walkthrough

This document summarizes the Energy Yield Service design, mathematical formulas, engineering assumptions, and integration with the core site analysis pipeline.

---

## 1. Files Created
1. **[app/services/energy_yield_service.py](file:///c:/Users/kanda/OneDrive/Documents/solar-wind-intelligence-api/AI-Solar-Wind-Deployment/app/services/energy_yield_service.py)**:
   - Houses the `EnergyYieldService` and calculations for solar, wind, and hybrid yields.
2. **[scratch/test_energy_yield.py](file:///c:/Users/kanda/OneDrive/Documents/solar-wind-intelligence-api/AI-Solar-Wind-Deployment/scratch/test_energy_yield.py)**:
   - Automated testing suite verifying scenario outputs, input changes (increasing yield checks), and pipeline integration.

---

## 2. Files Modified
1. **[schemas/analysis.py](file:///c:/Users/kanda/OneDrive/Documents/solar-wind-intelligence-api/AI-Solar-Wind-Deployment/schemas/analysis.py)**:
   - Extended `AnalysisRequest` with inputs for capacity (kW), efficiencies, and overrides.
   - Extended `AnalysisResponse` with output fields for solar, wind, hybrid, and recommended annual energy generation (kWh).
2. **[app/services/analysis_pipeline.py](file:///c:/Users/kanda/OneDrive/Documents/solar-wind-intelligence-api/AI-Solar-Wind-Deployment/app/services/analysis_pipeline.py)**:
   - Integrated the `EnergyYieldService` to evaluate yields sequentially at the end of the analysis workflow.

---

## 3. Architecture & Estimation Formulas

The energy yield calculation runs at the end of the Analysis Pipeline:

```
Feature Engineering (Solar/Wind Modules)
↓
ML Prediction (PredictionService suitability & recommendation)
↓
Technical Feasibility Engine (Constraint Validation & Soft Scoring)
↓
Energy Yield Estimation (Solar, Wind, Hybrid, and Recommended Calculations)
↓
Consolidated Response Output (AnalysisResponse payload)
```

### A. Solar Energy Yield Estimation
Consistently evaluates yield via the capacity factor ($CF_{solar}$):
\[E_{annual\_solar} = P_{installed\_capacity\_kw} \times 8760\ \text{hours/year} \times CF_{solar} \times \eta_{solar\_system\_efficiency}\]
* **Capacity Factor Derivation**:
  - If a custom `solar_capacity_factor` is provided in the request, use it.
  - If it is not provided, estimate it dynamically using the baseline daily peak-sun-hours rule:
    \[CF_{solar} = \max\left(0.0, \min\left(1.0, \frac{\text{Solar Irradiance}\ (kWh/m^2/day)}{24\ \text{hours/day}}\right)\right)\]

### B. Wind Energy Yield Estimation
Evaluates wind yield using wind speed-based capacity factor:
\[E_{annual\_wind} = P_{installed\_capacity\_kw} \times 8760\ \text{hours/year} \times CF_{wind} \times (1.0 - \text{losses}_{wind\_operational\_losses})\]
* **Capacity Factor Derivation**:
  - If a custom `wind_capacity_factor` is provided in the request, use it.
  - If it is not provided, estimate it dynamically using the average wind speed ($w$) baseline rule:
    \[CF_{wind} = \max\left(0.05, \min\left(0.50, 0.08 \times (w - 2.0)\right)\right)\]

### C. Hybrid Energy Yield Estimation
The hybrid facility is assumed to split its capacity 50/50 between solar and wind components:
\[E_{hybrid} = (E_{solar\_full\_capacity} + E_{wind\_full\_capacity}) \times 0.5 \times \eta_{hybrid\_efficiency}\]
* **Double Loss Avoidance**: Reuses pre-calculated yields (which already incorporate their respective efficiencies/losses) and applies a 5% integration/overlap efficiency adjustment ($\eta_{hybrid\_efficiency} = 0.95$) to the combined sum.

---

## 4. Engineering Assumptions & Bounds Validations

* **Estimate Quality**: These values represent baseline engineering estimates for planning and are not bankable resource assessments.
* **Sensible Input Bounds**: Inputs are validated to prevent non-sensical values:
  - `installed_capacity_kw` must be $> 0.0$.
  - efficiencies, losses, and capacity factors must be in the range $[0.0, 1.0]$.

---

## 5. Testing Performed

All test cases are verified in `scratch/test_energy_yield.py`:
* **Irradiance & Speed checks**: Verified that higher solar irradiance/wind speed yields higher output.
* **Factor changes**: Confirmed that increasing capacity factor, capacity, or system efficiency increases generation.
* **Pipeline integration**: Confirmed that `/analysis` endpoint computes and formats yields successfully.

---

## 6. Sample API Response (Unified `/analysis` Endpoint)

```json
{
  "project": {
    "project_name": "Odisha Hybrid Plant",
    "location": "Odisha Coast",
    "latitude": 19.8135,
    "longitude": 85.8312
  },
  "solar_features": {
    "solar_irradiance": 4.8816,
    "temperature": 26.81,
    "humidity": 74.25
  },
  "wind_features": {
    "wind_speed": 3.64,
    "wind_direction": 267.29,
    "wind_power_density": 182.24
  },
  "site_evaluation": {
    "resource_score": 45.67,
    "terrain_score": 95.0,
    "infrastructure_score": 90.0,
    "environmental_score": 65.0,
    "economic_score": 82.0
  },
  "site_score": {
    "overall_score": 71.18
  },
  "deployment_recommendation": {
    "deployment": "Solar",
    "confidence": 83,
    "reason": "Solar potential is good while wind resource is moderate."
  },
  "predicted_overall_score": 65.51,
  "predicted_deployment": "Solar",
  "top_features": [
    {
      "feature": "slope",
      "importance": 0.4936
    },
    {
      "feature": "wind_speed",
      "importance": 0.2194
    },
    {
      "feature": "protected_area_distance",
      "importance": 0.1213
    }
  ],
  "explanation": "Prediction is primarily influenced by slope and wind_speed.",
  "technical_feasibility": true,
  "technical_feasibility_score": 84,
  "constraint_violations": 0,
  "critical_violations": [],
  "overall_status": "Feasible",
  "solar_energy_yield_kwh": 1425427.2,
  "wind_energy_yield_kwh": 976915.2,
  "hybrid_energy_yield_kwh": 1141112.64,
  "recommended_annual_energy_kwh": 1425427.2
}
```
