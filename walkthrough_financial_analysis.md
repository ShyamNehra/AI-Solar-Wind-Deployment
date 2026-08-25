# Financial Analysis Module walkthrough

This document summarizes the Financial Analysis Service design, mathematical formulas, engineering assumptions, and integration with the core site analysis pipeline.

---

## 1. Files Created
1. **[app/services/financial_analysis_service.py](file:///c:/Users/kanda/OneDrive/Documents/solar-wind-intelligence-api/AI-Solar-Wind-Deployment/app/services/financial_analysis_service.py)**:
   - Houses the `FinancialAnalysisService` and calculations for annual revenue, project cost, payback period, and ROI.
2. **[scratch/test_financial_analysis.py](file:///c:/Users/kanda/OneDrive/Documents/solar-wind-intelligence-api/AI-Solar-Wind-Deployment/scratch/test_financial_analysis.py)**:
   - Automated testing suite verifying scenario outputs, input changes (increasing yield/tariff checks), edge cases, and pipeline integration.

---

## 2. Files Modified
1. **[schemas/analysis.py](file:///c:/Users/kanda/OneDrive/Documents/solar-wind-intelligence-api/AI-Solar-Wind-Deployment/schemas/analysis.py)**:
   - Extended `AnalysisRequest` with inputs for electricity tariff (INR/kWh), capital cost per kW, and additional installation percentage.
   - Extended `AnalysisResponse` with output fields for annual revenue, estimated project cost, payback period, and ROI.
2. **[app/services/analysis_pipeline.py](file:///c:/Users/kanda/OneDrive/Documents/solar-wind-intelligence-api/AI-Solar-Wind-Deployment/app/services/analysis_pipeline.py)**:
   - Integrated the `FinancialAnalysisService` to evaluate yields sequentially at the end of the analysis workflow.

---

## 3. Architecture & Estimation Formulas

The financial estimation runs at the end of the Analysis Pipeline:

```
Feature Engineering (Solar/Wind Modules)
↓
ML Prediction (PredictionService suitability & recommendation)
↓
Technical Feasibility Engine (Constraint Validation & Soft Scoring)
↓
Energy Yield Estimation (Solar, Wind, Hybrid Calculations)
↓
Financial Analysis (Revenue, Project Cost, Payback, and ROI Calculations)
↓
Consolidated Response Output (AnalysisResponse payload)
```

### A. Annual Revenue Estimation
\[\text{Annual Revenue (INR)} = \text{Recommended Annual Energy Yield (kWh)} \times \text{Electricity Tariff (INR/kWh)}\]

### B. Total Project Cost Estimation
Configurable base and installation costs:
\[\text{Total Project Cost (INR)} = \text{Installed Capacity (kW)} \times \text{Cost per kW} \times \left(1.0 + \frac{\text{Additional Installation \%}}{100.0}\right)\]

### C. Payback Period
Evaluates payback timeline in years:
\[\text{Payback Period (years)} = \frac{\text{Total Project Cost}}{\text{Annual Revenue}}\]
* **Edge-case Handling**: 
  - If annual revenue $\le 0$, payback period is undefined/infinite (returns `-1.0`).
  - If project cost $= 0$, payback period is immediate (returns `0.0`).

### D. Return on Investment (ROI)
Annual Return on Capital Investment ratio:
\[\text{ROI (\%)} = \left(\frac{\text{Annual Revenue}}{\text{Total Project Cost}}\right) \times 100\]
* **Edge-case Handling**:
  - If project cost $\le 0$, ROI is undefined (returns `-1.0`).

---

## 4. Engineering Assumptions & Default Values

* **Electricity Tariff**: Defaults to ₹7.0 / kWh.
* **Capital Cost per kW**: Defaults to ₹25,000 / kW.
* **Additional Installation Percentage**: Defaults to 10%.
* **Estimate Quality**: These values represent baseline planning estimates and are not bankable financial resource assessments.

---

## 5. Testing Performed

All test cases are verified in `scratch/test_financial_analysis.py`:
* **Revenue & Cost checks**: Verified that higher annual energy yield/tariff increases revenue, and larger capacity/cost per kW increases project cost.
* **Edge Cases**: Verified that zero/negative revenues return `-1.0` payback, and zero project costs return `-1.0` ROI.
* **Pipeline integration**: Confirmed that `/analysis` endpoint computes and formats financials successfully.

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
    "terrain_score": 96.0,
    "infrastructure_score": 94.8,
    "environmental_score": 50.0,
    "economic_score": 77.5
  },
  "site_score": {
    "overall_score": 69.45
  },
  "deployment_recommendation": {
    "deployment": "Solar",
    "confidence": 83,
    "reason": "Solar potential is good while wind resource is moderate."
  },
  "predicted_overall_score": 62.72,
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
  "technical_feasibility_score": 83,
  "constraint_violations": 0,
  "critical_violations": [],
  "overall_status": "Feasible",
  "solar_energy_yield_kwh": 1425427.2,
  "wind_energy_yield_kwh": 976915.2,
  "hybrid_energy_yield_kwh": 1141112.64,
  "recommended_annual_energy_kwh": 1425427.2,
  "annual_revenue": 9977990.4,
  "estimated_project_cost": 27500000.0,
  "payback_period": 2.76,
  "roi": 36.28
}
```
