<!-- Initial database tables:
Users
Projects
Sites
EnvironmentalData
SolarPrediction
WindPrediction
SuitabilityScore
Reports
For each table, documented:
Primary Key
Important Columns -->


## Users
#### user_id
#### full_name
#### email
#### password_hash
#### role (Renewable Energy Planner, GIS Analyst, Project Manager, Admin)
#### created_at
#### last_login



## Projects
project_id
project_name
created_by (references Users.user_id)
region
project_type (solar, wind, hybrid)
status (draft, active, completed)
created_at



## Sites

site_id
project_id (references Projects.project_id)
latitude
longitude
region
land_area_sqm
elevation_m
land_ownership
existing_infrastructure
created_at



## EnvironmentalData

env_data_id
site_id (references Sites.site_id)
data_source (NASA_POWER, GWA, SRTM, Sentinel, OSM)
solar_irradiance
wind_speed
temperature
rainfall
cloud_cover
slope_percent
land_cover_type
recorded_date



## SolarPrediction

solar_prediction_id
site_id (references Sites.site_id)
annual_irradiance
peak_sun_hours
expected_energy_output_kwh
capacity_factor
performance_ratio
model_version
predicted_at



## WindPrediction

wind_prediction_id
site_id (references Sites.site_id)
average_wind_speed
wind_power_density
turbulence_intensity
capacity_factor
expected_annual_energy_kwh
model_version
predicted_at



## SuitabilityScore

score_id
site_id (references Sites.site_id)
resource_score
geographic_score
infrastructure_score
environmental_score
economic_score
overall_score
suitability_category (Excellent, Highly Suitable, Moderately Suitable, Low Suitability, Unsuitable)
calculated_at



## Reports

report_id
project_id (references Projects.project_id)
site_id (references Sites.site_id, nullable)
report_type (site_assessment, solar_potential, wind_potential, feasibility, investment)
file_format (PDF, Excel)
file_path
generated_by (references Users.user_id)
generated_at