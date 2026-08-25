# Technical Feasibility Module walkthrough

This document summarizes the Technical Feasibility Engine design, integration with the ML and site analysis pipelines, and execution of automated validations.

---

## 1. Files Created
1. **[app/services/feasibility_engine.py](file:///c:/Users/kanda/OneDrive/Documents/solar-wind-intelligence-api/AI-Solar-Wind-Deployment/app/services/feasibility_engine.py)**:
   - Houses the Technical Feasibility Engine.
   - Methods: `validate_hard_constraints()`, `calculate_soft_constraint_score()`, `evaluate_site()`.
2. **[scratch/test_feasibility.py](file:///c:/Users/kanda/OneDrive/Documents/solar-wind-intelligence-api/AI-Solar-Wind-Deployment/scratch/test_feasibility.py)**:
   - Automated unit and integration testing suite verifying multiple site profiles, hard violations, soft variations, and pipeline integrations.

---

## 2. Files Modified
1. **[schemas/analysis.py](file:///c:/Users/kanda/OneDrive/Documents/solar-wind-intelligence-api/AI-Solar-Wind-Deployment/schemas/analysis.py)**:
   - Extended `AnalysisResponse` schema to support feasibility outputs and consolidated ML prediction results.
2. **[app/services/analysis_pipeline.py](file:///c:/Users/kanda/OneDrive/Documents/solar-wind-intelligence-api/AI-Solar-Wind-Deployment/app/services/analysis_pipeline.py)**:
   - Integrated the Technical Feasibility Engine and ML prediction modules into the core site analysis pipeline workflow.

---

## 3. Architecture & Constraint Logic

The feasibility flow runs immediately after retrieving features and executing ML predictions:

```
Feature Engineering (Solar/Wind Modules)
↓
ML Prediction (PredictionService suitability & recommendation)
↓
Technical Feasibility Engine (Constraint Validation & Soft Scoring)
↓
Consolidated Response Output (AnalysisResponse payload)
```

### A. Mandatory Hard Constraints (Critical Rejections)
A site is flagged as `technical_feasibility = false` and `overall_status = "Unfeasible"` if any of the following mandatory conditions fail:
- **Terrain Slope**: Slope must be $\le 20$ degrees.
- **Proximity to Protected Areas**: Distance to protected area boundary must be $\ge 2$ km.
- **Site Elevation**: Elevation must be $\le 3000$ meters.
- **Environmental Impact Index**: Overall environmental impact rating must be $\le 8.0$ (out of 10).

### B. Soft Constraints Scoring
Soft constraints reduce the feasibility score but do *not* reject the site. They are evaluated by reusing the existing normalization logic from the scoring engine:
- Proximity to electrical grid (`normalize_distance_grid`, weight: 25%)
- Proximity to roads (`normalize_distance_road`, weight: 20%)
- Terrain slope (`normalize_slope`, weight: 20%)
- Environmental score (`calculate_environmental_score`, weight: 20%)
- Economic factors (`calculate_economic_score`, weight: 15%)

Formula:
\[\text{Feasibility Score} = \text{Grid} \times 0.25 + \text{Road} \times 0.20 + \text{Slope} \times 0.20 + \text{Environmental} \times 0.20 + \text{Economic} \times 0.15\]

---

## 4. Testing Performed

All test cases are fully implemented and verified in `scratch/test_feasibility.py`:
* **Valid site validation**: Verified that sites with flat slope, low protected area proximity, and close infrastructure receive `overall_status = "Feasible"` and high scores ($>70$).
* **Hard constraint validation**: Tested slope limit violation (>20 degrees) and protected area violation (<2km). Asserts that the engine correctly flags `technical_feasibility = false` and lists violated constraints.
* **Soft constraints scoring variance**: Tested a remote, high-cost site to verify that its score drops ($29$) but the site remains feasible (since no hard limits are breached).
* **Pipeline Integration**: Verified unified endpoint output keys match the extended schemas.

---

## 5. Sample API Response (Unified `/analysis` Endpoint)

```json
{
  "project": {
    "project_name": "Odisha Coastal Wind & Solar",
    "location": "Puri District",
    "latitude": 19.8135,
    "longitude": 85.8312
  },
  "solar_features": {
    "solar_irradiance": 5.4,
    "temperature": 28.5,
    "humidity": 62.0
  },
  "wind_features": {
    "wind_speed": 2.64,
    "wind_direction": 224.0,
    "wind_power_density": 132.0
  },
  "site_evaluation": {
    "resource_score": 48.75,
    "terrain_score": 96.0,
    "infrastructure_score": 83.2,
    "environmental_score": 35.5,
    "economic_score": 80.88
  },
  "site_score": {
    "overall_score": 68.39
  },
  "deployment_recommendation": {
    "deployment": "Solar",
    "confidence": 75,
    "reason": "Dominant solar potential detected with moderate wind resources."
  },
  "predicted_overall_score": 62.23,
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
  "technical_feasibility_score": 78,
  "constraint_violations": 0,
  "critical_violations": [],
  "overall_status": "Feasible"
}
```
