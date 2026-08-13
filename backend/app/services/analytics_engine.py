from app.models.environmental_data import EnvironmentalData


def calculate_solar_suitability(env: EnvironmentalData) -> float:
    """Calculate Solar suitability score (0 - 100)."""
    irradiance = env.solar_irradiance_kwh_m2 or 0.0
    slope = env.land_slope_deg or 2.0
    temp = env.temperature_c or 25.0

    # Solar Irradiance Score (Optimal: > 5.5 kWh/m2/day)
    irradiance_score = min(100.0, (irradiance / 6.0) * 100.0)

    # Slope Score (Flat land < 5 deg is ideal)
    slope_score = max(0.0, 100.0 - (slope * 5.0))

    # Temperature Efficiency Factor (Panels lose efficiency > 25°C)
    temp_score = 100.0 if temp <= 25.0 else max(50.0, 100.0 - (temp - 25.0) * 2.0)

    return round((0.60 * irradiance_score) + (0.25 * slope_score) + (0.15 * temp_score), 2)


def calculate_wind_suitability(env: EnvironmentalData) -> float:
    """Calculate Wind suitability score (0 - 100)."""
    wind_speed = env.wind_speed_ms or 0.0
    elevation = env.elevation_m or 100.0

    # Wind Speed Score (Cut-in ~3m/s, optimal >= 7.5m/s)
    if wind_speed < 3.0:
        wind_score = 10.0
    else:
        wind_score = min(100.0, ((wind_speed - 3.0) / 5.0) * 100.0)

    # Elevation Score (Higher altitude usually means better wind potential)
    elevation_score = min(100.0, (elevation / 1000.0) * 100.0)

    return round((0.80 * wind_score) + (0.20 * elevation_score), 2)


def calculate_infrastructure_score(env: EnvironmentalData) -> float:
    """Calculate Infrastructure & Logistics score (0 - 100)."""
    dist_road = env.distance_to_roads_km or 20.0
    dist_grid = env.distance_to_grid_km or 20.0

    road_score = max(0.0, 100.0 - (dist_road * 3.0))
    grid_score = max(0.0, 100.0 - (dist_grid * 2.5))

    return round((0.50 * road_score) + (0.50 * grid_score), 2)


def evaluate_site_suitability(env: EnvironmentalData) -> dict:
    """Evaluate full site suitability using multi-criteria weighted scoring."""
    solar_score = calculate_solar_suitability(env)
    wind_score = calculate_wind_suitability(env)
    infra_score = calculate_infrastructure_score(env)

    # Hybrid overall score weighted formula
    overall_score = round(
        (0.35 * max(solar_score, wind_score)) +
        (0.25 * min(solar_score, wind_score)) +
        (0.20 * infra_score) +
        (0.10 * 85.0) +  # Environmental baseline
        (0.10 * 80.0),   # Economic baseline
        2
    )

    # Determine recommended project classification
    if solar_score >= 70.0 and wind_score >= 70.0:
        recommendation = "Optimal for Hybrid Solar-Wind Farm"
    elif solar_score >= 65.0:
        recommendation = "Optimal for Solar PV Farm"
    elif wind_score >= 65.0:
        recommendation = "Optimal for Wind Turbine Farm"
    else:
        recommendation = "Sub-optimal: Infrastructure or Resource Upgrades Required"

    # Identify site risks
    risks = []
    if env.distance_to_grid_km and env.distance_to_grid_km > 15.0:
        risks.append("High grid interconnection distance will increase CAPEX.")
    if env.temperature_c and env.temperature_c > 35.0:
        risks.append("High ambient temperatures may reduce solar panel efficiency.")
    if env.wind_speed_ms and env.wind_speed_ms < 4.5:
        risks.append("Low average wind speed reduces standalone wind power viability.")

    return {
        "overall_score": overall_score,
        "solar_score": solar_score,
        "wind_score": wind_score,
        "infrastructure_score": infra_score,
        "recommendation": recommendation,
        "risks": risks
    }