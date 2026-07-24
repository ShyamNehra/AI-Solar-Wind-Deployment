"""
Optimization Constants for Solar & Wind Deployment Intelligence Platform.
Contains configurable thresholds and constants for capacity planning and expansion analysis.
"""

# Default capacity densities in kW per square meter of land area
DEFAULT_SOLAR_DENSITY = 0.15  # 150 kW per 1000 m²
DEFAULT_WIND_DENSITY = 0.05   # 50 kW per 1000 m²

# Default expansion analysis thresholds
EXPANSION_THRESHOLDS = {
    "expandable_land": 5000.0,            # square meters
    "limited_land": 1000.0,               # square meters
    "min_environmental_score": 80.0,      # score out of 100
    "min_infrastructure_score": 70.0,     # score out of 100
    "limited_environmental_score": 50.0,  # score out of 100
    "limited_infrastructure_score": 50.0, # score out of 100
}
