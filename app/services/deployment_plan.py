from app.services.optimization_engine import optimize_deployment_strategy
from app.services.capacity_planning import plan_installation_capacity
from app.services.expansion_analysis import analyze_expansion_feasibility


def generate_deployment_plan(
    site_details: dict,
    custom_config: dict = None
) -> dict:
    """
    Generate a structured deployment plan consuming outputs from previously implemented services.

    Args:
        site_details (dict): Site features (solar_irradiance, wind_speed, land_area, etc.).
        custom_config (dict, optional): Custom configuration thresholds.

    Returns:
        dict: Detailed deployment plan profile.
    """
    solar = float(site_details.get("solar_irradiance", 0.0))
    wind = float(site_details.get("wind_speed", 0.0))
    land = float(site_details.get("land_area", 0.0))
    remaining = float(site_details.get("remaining_land", 0.0))
    env_score = float(site_details.get("environmental_score", 100.0))
    inf_score = float(site_details.get("infrastructure_score", 100.0))

    # 1. Optimize deployment strategy
    strategy = optimize_deployment_strategy(solar, wind)
    tech = strategy["optimized_technology"]
    remarks = strategy["strategy_remarks"]

    # 2. Plan installation capacity
    capacity = plan_installation_capacity(land, solar, wind, custom_config)

    # 3. Analyze expansion feasibility
    expansion = analyze_expansion_feasibility(remaining, env_score, inf_score, custom_config)

    return {
        "recommended_technology": tech,
        "recommended_capacity_kw": capacity,
        "expansion_status": expansion,
        "optimization_remarks": remarks
    }
