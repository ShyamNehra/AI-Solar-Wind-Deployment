"""
Constraint validation for renewable energy site evaluation.

Each function returns True if the constraint is satisfied,
otherwise False.

Threshold values are defined as constants so they can be
changed easily without modifying the validation logic.
"""

# ==========================
# Configurable Thresholds
# ==========================

MAX_SLOPE = 15.0                    # degrees
MIN_SOLAR_IRRADIANCE = 5.0          # kWh/m²/day
MIN_WIND_SPEED = 5.0                # m/s
MAX_DISTANCE_TO_GRID = 20.0         # km
MAX_DISTANCE_TO_ROAD = 10.0         # km


# ==========================
# Constraint Functions
# ==========================

def check_slope(slope: float) -> bool:
    """Return True if slope is within the allowed limit."""
    return slope <= MAX_SLOPE


def check_solar_irradiance(solar_irradiance: float) -> bool:
    """Return True if solar irradiance meets the minimum requirement."""
    return solar_irradiance >= MIN_SOLAR_IRRADIANCE


def check_wind_speed(wind_speed: float) -> bool:
    """Return True if wind speed meets the minimum requirement."""
    return wind_speed >= MIN_WIND_SPEED


def check_grid_distance(distance_to_grid: float) -> bool:
    """Return True if the grid is close enough."""
    return distance_to_grid <= MAX_DISTANCE_TO_GRID


def check_road_distance(distance_to_road: float) -> bool:
    """Return True if the road is close enough."""
    return distance_to_road <= MAX_DISTANCE_TO_ROAD