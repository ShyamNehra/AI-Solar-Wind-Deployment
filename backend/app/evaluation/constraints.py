# Configurable Threshold Constants
MAX_ALLOWED_SLOPE = 15.0        # Max terrain angle in degrees
MIN_SOLAR_IRRADIANCE = 3.5      # Min daily average solar solar (kWh/m2/day)
MIN_WIND_SPEED = 4.5            # Min average wind speed at 100m (m/s)
MAX_GRID_DISTANCE_M = 50000.0   # 50 km max to transmission grid lines
MAX_ROAD_DISTANCE_M = 15000.0   # 15 km max to logistics routes

def check_slope_constraint(slope: float) -> bool:
    return slope <= MAX_ALLOWED_SLOPE

def check_solar_constraint(solar: float) -> bool:
    return solar >= MIN_SOLAR_IRRADIANCE

def check_wind_constraint(wind: float) -> bool:
    return wind >= MIN_WIND_SPEED

def check_grid_distance_constraint(distance: float) -> bool:
    return distance <= MAX_GRID_DISTANCE_M

def check_road_distance_constraint(distance: float) -> bool:
    return distance <= MAX_ROAD_DISTANCE_M

def evaluate_all_constraints(features: dict) -> tuple[bool, list[str]]:
    """
    Evaluates a feature dictionary against all configurable hard rules.
    Returns:
        (is_valid, list_of_failed_constraint_reasons)
    """
    failed_constraints = []

    if not check_slope_constraint(features.get("slope", 0.0)):
        failed_constraints.append(f"Terrain slope too steep: {features.get('slope')}° (Max: {MAX_ALLOWED_SLOPE}°)")
        
    if not check_solar_constraint(features.get("solar_irradiance", 0.0)):
        failed_constraints.append(f"Insufficient solar resource: {features.get('solar_irradiance')} kWh/m2 (Min: {MIN_SOLAR_IRRADIANCE})")
        
    if not check_wind_constraint(features.get("wind_speed", 0.0)):
        failed_constraints.append(f"Insufficient wind resource: {features.get('wind_speed')} m/s (Min: {MIN_WIND_SPEED})")
        
    if not check_grid_distance_constraint(features.get("grid_distance", 0.0)):
        failed_constraints.append(f"Too far from power grid: {features.get('grid_distance')}m (Max: {MAX_GRID_DISTANCE_M}m)")
        
    if not check_road_distance_constraint(features.get("road_distance", 0.0)):
        failed_constraints.append(f"Too far from access road: {features.get('road_distance')}m (Max: {MAX_ROAD_DISTANCE_M}m)")

    is_valid = len(failed_constraints) == 0
    return is_valid, failed_constraints