# Database Design

## Overview

The database stores user information, renewable energy projects, environmental data, prediction results, and generated reports. It is designed to support solar and wind energy site suitability analysis.

---

# 1. Users

**Primary Key:** `user_id`

| Column | Data Type | Description |
|---------|-----------|-------------|
| user_id | INT | Unique user ID |
| name | VARCHAR(100) | Full name |
| email | VARCHAR(100) | Email address |
| password_hash | VARCHAR(255) | Encrypted password |
| role | VARCHAR(20) | Admin/User |
| created_at | TIMESTAMP | Registration date |

---

# 2. Projects

**Primary Key:** `project_id`

| Column | Data Type | Description |
|---------|-----------|-------------|
| project_id | INT | Unique project ID |
| user_id | INT | Owner of project |
| project_name | VARCHAR(150) | Project title |
| description | TEXT | Project description |
| created_at | TIMESTAMP | Creation time |

**Foreign Key**
- user_id → Users.user_id

---

# 3. Sites

**Primary Key:** `site_id`

| Column | Data Type | Description |
|---------|-----------|-------------|
| site_id | INT | Unique site ID |
| project_id | INT | Associated project |
| location_name | VARCHAR(100) | Site name |
| latitude | DECIMAL(10,6) | Latitude |
| longitude | DECIMAL(10,6) | Longitude |
| state | VARCHAR(100) | State |
| country | VARCHAR(100) | Country |

**Foreign Key**
- project_id → Projects.project_id

---

# 4. EnvironmentalData

**Primary Key:** `environment_id`

| Column | Data Type | Description |
|---------|-----------|-------------|
| environment_id | INT | Unique record ID |
| site_id | INT | Site reference |
| temperature | FLOAT | Average temperature |
| rainfall | FLOAT | Rainfall |
| wind_speed | FLOAT | Wind speed |
| solar_radiation | FLOAT | Solar radiation |
| humidity | FLOAT | Humidity |
| year | INT | Observation year |

**Foreign Key**
- site_id → Sites.site_id

---

# 5. SolarPrediction

**Primary Key:** `solar_prediction_id`

| Column | Data Type | Description |
|---------|-----------|-------------|
| solar_prediction_id | INT | Prediction ID |
| site_id | INT | Site reference |
| predicted_output | FLOAT | Expected solar output |
| efficiency | FLOAT | Efficiency percentage |
| prediction_date | DATE | Prediction date |

**Foreign Key**
- site_id → Sites.site_id

---

# 6. WindPrediction

**Primary Key:** `wind_prediction_id`

| Column | Data Type | Description |
|---------|-----------|-------------|
| wind_prediction_id | INT | Prediction ID |
| site_id | INT | Site reference |
| predicted_output | FLOAT | Expected wind output |
| average_speed | FLOAT | Average wind speed |
| prediction_date | DATE | Prediction date |

**Foreign Key**
- site_id → Sites.site_id

---

# 7. SuitabilityScore

**Primary Key:** `score_id`

| Column | Data Type | Description |
|---------|-----------|-------------|
| score_id | INT | Score ID |
| site_id | INT | Site reference |
| solar_score | FLOAT | Solar suitability |
| wind_score | FLOAT | Wind suitability |
| overall_score | FLOAT | Combined score |
| recommendation | VARCHAR(100) | Best renewable source |

**Foreign Key**
- site_id → Sites.site_id

---

# 8. Reports

**Primary Key:** `report_id`

| Column | Data Type | Description |
|---------|-----------|-------------|
| report_id | INT | Report ID |
| project_id | INT | Related project |
| report_name | VARCHAR(150) | Report title |
| generated_date | TIMESTAMP | Date generated |
| report_path | VARCHAR(255) | PDF/File location |

**Foreign Key**
- project_id → Projects.project_id

---

# Entity Relationships

Users (1) ---- (M) Projects

Projects (1) ---- (M) Sites

Sites (1) ---- (M) EnvironmentalData

Sites (1) ---- (1) SolarPrediction

Sites (1) ---- (1) WindPrediction

Sites (1) ---- (1) SuitabilityScore

Projects (1) ---- (M) Reports