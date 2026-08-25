"""
Energy Estimation Module for Solar & Wind Deployment Intelligence Platform.
Computes annual energy production using standard capacity factor equations.
"""

# Constant representing hours in a standard non-leap year
HOURS_PER_YEAR = 8760


def estimate_solar_energy(installed_capacity: float, capacity_factor: float) -> float:
    """
    Estimate the annual energy output for a solar installation.
    Formula: Annual Energy = Installed Capacity * Capacity Factor * 8760

    Args:
        installed_capacity (float): Installed solar capacity in kW.
        capacity_factor (float): Solar capacity factor (ratio between 0.0 and 1.0).

    Returns:
        float: Estimated annual solar energy output in kWh.
    """
    # Ensure inputs are non-negative
    capacity = max(0.0, installed_capacity)
    cf = max(0.0, min(1.0, capacity_factor))
    return round(capacity * cf * HOURS_PER_YEAR, 2)


def estimate_wind_energy(installed_capacity: float, capacity_factor: float) -> float:
    """
    Estimate the annual energy output for a wind installation.
    Formula: Annual Energy = Installed Capacity * Capacity Factor * 8760

    Args:
        installed_capacity (float): Installed wind capacity in kW.
        capacity_factor (float): Wind capacity factor (ratio between 0.0 and 1.0).

    Returns:
        float: Estimated annual wind energy output in kWh.
    """
    # Ensure inputs are non-negative
    capacity = max(0.0, installed_capacity)
    cf = max(0.0, min(1.0, capacity_factor))
    return round(capacity * cf * HOURS_PER_YEAR, 2)


def estimate_site_energy(
    deployment_type: str,
    installed_capacity: float,
    solar_cf: float,
    wind_cf: float
) -> dict[str, float]:
    """
    Service function that evaluates energy production based on the site's deployment type.

    Args:
        deployment_type (str): Deployment strategy ("Solar", "Wind", "Hybrid", or "None").
        installed_capacity (float): Total installed capacity in kW.
        solar_cf (float): Capacity factor for solar.
        wind_cf (float): Capacity factor for wind.

    Returns:
        dict: Breakdown of annual solar, wind, and total energy in kWh.
    """
    annual_solar = 0.0
    annual_wind = 0.0

    # Ensure capacity is clean
    capacity = max(0.0, installed_capacity)

    if deployment_type == "Solar":
        annual_solar = estimate_solar_energy(capacity, solar_cf)
    elif deployment_type == "Wind":
        annual_wind = estimate_wind_energy(capacity, wind_cf)
    elif deployment_type == "Hybrid":
        # For hybrid, assume capacity is split equally or applies individually.
        # Following the mentor requirement: Combined Energy = Solar Energy + Wind Energy
        # We estimate solar and wind using their respective capacity factors and total capacity.
        # To avoid duplicating logic, we call our helper functions directly.
        annual_solar = estimate_solar_energy(capacity, solar_cf)
        annual_wind = estimate_wind_energy(capacity, wind_cf)

    total_energy = round(annual_solar + annual_wind, 2)

    return {
        "annual_solar_energy": annual_solar,
        "annual_wind_energy": annual_wind,
        "total_annual_energy": total_energy
    }


def estimate_site_energy_from_strategy(
    strategy_result: dict,
    installed_capacity: float,
    solar_cf: float,
    wind_cf: float
) -> dict[str, float]:
    """
    Helper function integrating deployment recommendation results directly.

    Args:
        strategy_result (dict): Recommendation profile (e.g. from recommend_deployment()).
        installed_capacity (float): Capacity in kW.
        solar_cf (float): Solar capacity factor.
        wind_cf (float): Wind capacity factor.

    Returns:
        dict: Energy estimation breakdown.
    """
    deployment_type = strategy_result.get("deployment", "None")
    return estimate_site_energy(deployment_type, installed_capacity, solar_cf, wind_cf)
