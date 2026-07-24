from app.services.optimization_constants import DEFAULT_SOLAR_DENSITY, DEFAULT_WIND_DENSITY


def plan_installation_capacity(
    land_area: float,
    solar_irradiance: float,
    wind_speed: float,
    custom_config: dict = None
) -> float:
    """
    Plan the recommended installation capacity in kW based on land area and resource strengths.

    Args:
        land_area (float): Available land area in square meters.
        solar_irradiance (float): Solar irradiance in kWh/m²/day.
        wind_speed (float): Wind speed in m/s.
        custom_config (dict, optional): Configuration dictionary to override defaults.

    Returns:
        float: Recommended installation capacity in kW (rounded to 2 decimal places).
    """
    config = custom_config or {}
    solar_density = config.get("solar_density", DEFAULT_SOLAR_DENSITY)
    wind_density = config.get("wind_density", DEFAULT_WIND_DENSITY)

    # Scaling factors based on resource availability / quality thresholds
    solar_factor = max(0.0, min(1.0, solar_irradiance / 8.0)) if solar_irradiance >= 3.0 else 0.0
    wind_factor = max(0.0, min(1.0, wind_speed / 12.0)) if wind_speed >= 3.0 else 0.0

    # Capacity calculations: Capacity = Area * Density * Resource Quality Factor
    solar_capacity = land_area * solar_density * solar_factor
    wind_capacity = land_area * wind_density * wind_factor

    # Aggregate capacity recommendation (Hybrid capacity assumes combined allocation, otherwise dominant)
    if solar_irradiance >= 4.5 and wind_speed >= 5.0:
        recommended_capacity = solar_capacity + wind_capacity
    elif solar_irradiance >= wind_speed:  # solar-dominant resource
        recommended_capacity = solar_capacity
    else:  # wind-dominant resource
        recommended_capacity = wind_capacity

    return round(max(0.0, recommended_capacity), 2)
