# Database Design Draft

## Project
AI-Powered Solar & Wind Deployment Intelligence Platform

---

# 1. Users

### Primary Key
- user_id

### Important Columns
- user_id
- full_name
- email
- password_hash
- role
- created_at

---

# 2. Projects

### Primary Key
- project_id

### Important Columns
- project_id
- project_name
- description
- created_by
- created_at
- status

---

# 3. Sites

### Primary Key
- site_id

### Important Columns
- site_id
- project_id
- site_name
- latitude
- longitude
- district
- state
- elevation

---

# 4. EnvironmentalData

### Primary Key
- environmental_data_id

### Important Columns
- environmental_data_id
- site_id
- solar_irradiance
- wind_speed
- temperature
- rainfall
- slope
- land_cover
- data_source
- collected_at

---

# 5. SolarPrediction

### Primary Key
- solar_prediction_id

### Important Columns
- solar_prediction_id
- site_id
- predicted_generation
- efficiency_score
- confidence_score
- prediction_date

---

# 6. WindPrediction

### Primary Key
- wind_prediction_id

### Important Columns
- wind_prediction_id
- site_id
- predicted_generation
- average_wind_speed
- confidence_score
- prediction_date

---

# 7. SuitabilityScore

### Primary Key
- suitability_score_id

### Important Columns
- suitability_score_id
- site_id
- solar_score
- wind_score
- terrain_score
- accessibility_score
- overall_score
- recommendation

---

# 8. Reports

### Primary Key
- report_id

### Important Columns
- report_id
- project_id
- report_name
- generated_by
- generated_at
- report_type
- report_path

---

# Summary

| Table | Primary Key |
|--------|-------------|
| Users | user_id |
| Projects | project_id |
| Sites | site_id |
| EnvironmentalData | environmental_data_id |
| SolarPrediction | solar_prediction_id |
| WindPrediction | wind_prediction_id |
| SuitabilityScore | suitability_score_id |
| Reports | report_id |
This document outlines the relational database design for the Solar & Wind Deployment Intelligence Platform. 

```mermaid
erDiagram
    USERS ||--o{ PROJECTS : owns
    PROJECTS ||--o{ SITES : contains
    SITES ||--|| ENVIRONMENTAL_DATA : measures
    SITES ||--|| SUITABILITY_SCORES : calculates
    SITES ||--o{ SOLAR_PREDICTIONS : predicts
    SITES ||--o{ WIND_PREDICTIONS : predicts
    PROJECTS ||--o{ REPORTS : compiles
```

---

## 1. `Users` Table
Stores login credentials and access levels for secure operations.
* **Primary Key**: `user_id` (UUID)
* **Columns**:
  - `user_id` (UUID, Primary Key)
  - `email` (VARCHAR, Unique, Indexed)
  - `hashed_password` (VARCHAR)
  - `full_name` (VARCHAR)
  - `role` (VARCHAR)
  - `created_at` (TIMESTAMP)

---

## 2. `Projects` Table
Represents configuration settings and parameters for a deployment assessment.
* **Primary Key**: `project_id` (UUID)
* **Foreign Key**: `user_id` references `Users(user_id)`
* **Columns**:
  - `project_id` (UUID, Primary Key)
  - `user_id` (UUID, Foreign Key)
  - `name` (VARCHAR)
  - `description` (TEXT)
  - `created_at` (TIMESTAMP)

---

## 3. `Sites` Table
Stores geographical candidates evaluated for solar-wind installation suitability.
* **Primary Key**: `site_id` (UUID)
* **Foreign Key**: `project_id` references `Projects(project_id)`
* **Columns**:
  - `site_id` (UUID, Primary Key)
  - `project_id` (UUID, Foreign Key)
  - `name` (VARCHAR)
  - `latitude` (DECIMAL(9,6))
  - `longitude` (DECIMAL(9,6))
  - `area_sq_m` (DECIMAL)
  - `created_at` (TIMESTAMP)

---

## 4. `EnvironmentalData` Table
Caches geological constraints and elevation mappings from SRTM/Sentinel/OSM.
* **Primary Key**: `env_data_id` (UUID)
* **Foreign Key**: `site_id` references `Sites(site_id)`
* **Columns**:
  - `env_data_id` (UUID, Primary Key)
  - `site_id` (UUID, Foreign Key)
  - `elevation_m` (DECIMAL)
  - `slope_degrees` (DECIMAL)
  - `land_cover_class` (VARCHAR)
  - `dist_to_road_m` (DECIMAL)
  - `dist_to_substation_m` (DECIMAL)
  - `updated_at` (TIMESTAMP)

---

## 5. `SolarPrediction` Table
Caches day-by-day solar predictions derived from NASA POWER datasets.
* **Primary Key**: `solar_pred_id` (UUID)
* **Foreign Key**: `site_id` references `Sites(site_id)`
* **Columns**:
  - `solar_pred_id` (UUID, Primary Key)
  - `site_id` (UUID, Foreign Key)
  - `prediction_date` (DATE)
  - `expected_ghi` (DECIMAL)  -- Global Horizontal Irradiance
  - `predicted_solar_yield_kwh` (DECIMAL)
  - `confidence_score` (DECIMAL)

---

## 6. `WindPrediction` Table
Caches wind speed predictions and energy generation yield forecasts.
* **Primary Key**: `wind_pred_id` (UUID)
* **Foreign Key**: `site_id` references `Sites(site_id)`
* **Columns**:
  - `wind_pred_id` (UUID, Primary Key)
  - `site_id` (UUID, Foreign Key)
  - `prediction_date` (DATE)
  - `average_wind_speed_ms` (DECIMAL)
  - `predicted_wind_yield_kwh` (DECIMAL)
  - `confidence_score` (DECIMAL)

---

## 7. `SuitabilityScore` Table
Holds multi-criteria optimization indices calculated for wind and solar suitability.
* **Primary Key**: `score_id` (UUID)
* **Foreign Key**: `site_id` references `Sites(site_id)`
* **Columns**:
  - `score_id` (UUID, Primary Key)
  - `site_id` (UUID, Foreign Key)
  - `solar_score` (DECIMAL(5,2))      -- Out of 100
  - `wind_score` (DECIMAL(5,2))       -- Out of 100
  - `infrastructure_score` (DECIMAL(5,2)) -- Out of 100
  - `overall_suitability_score` (DECIMAL(5,2))
  - `evaluated_at` (TIMESTAMP)

---

## 8. `Reports` Table
Compiles final analysis PDFs/Excel metadata generated for export.
* **Primary Key**: `report_id` (UUID)
* **Foreign Key**: `project_id` references `Projects(project_id)`
* **Columns**:
  - `report_id` (UUID, Primary Key)
  - `project_id` (UUID, Foreign Key)
  - `report_type` (VARCHAR)  -- e.g. "PDF", "XLSX"
  - `file_path` (VARCHAR)
  - `generated_at` (TIMESTAMP)
