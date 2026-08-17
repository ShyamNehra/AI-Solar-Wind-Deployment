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