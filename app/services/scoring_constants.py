"""
Scoring Constants for Solar & Wind Deployment Intelligence Platform.
Contains configurable weights and parameter normalization bounds.
"""

# Configurable Default Category Weights (must sum to 1.0)
DEFAULT_CATEGORY_WEIGHTS: dict[str, float] = {
    "resource": 0.35,        # 35%
    "terrain": 0.25,         # 25%
    "infrastructure": 0.15,  # 15%
    "environmental": 0.15,   # 15%
    "economic": 0.10,        # 10%
}

# Parameter Normalization Bounds (min_val, max_val)
SOLAR_IRRADIANCE_BOUNDS = (0.0, 8.0)     # kWh/m²/day
WIND_SPEED_BOUNDS = (0.0, 12.0)           # m/s
SLOPE_BOUNDS = (0.0, 30.0)                # degrees (0 = flat = best)
GRID_DISTANCE_BOUNDS = (0.0, 50.0)        # km (0 = adjacent = best)
ROAD_DISTANCE_BOUNDS = (0.0, 20.0)        # km (0 = adjacent = best)
