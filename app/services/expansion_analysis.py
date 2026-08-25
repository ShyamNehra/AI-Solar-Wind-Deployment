from app.services.optimization_constants import EXPANSION_THRESHOLDS


def analyze_expansion_feasibility(
    remaining_land: float,
    environmental_score: float,
    infrastructure_score: float,
    custom_config: dict = None
) -> str:
    """
    Evaluate expansion feasibility returning one of: Expandable, Limited Expansion, Not Expandable.

    Args:
        remaining_land (float): Remaining land area in square meters.
        environmental_score (float): Score (0-100) indicating environmental suitability (higher is safer).
        infrastructure_score (float): Score (0-100) indicating infrastructure capacity (higher is better).
        custom_config (dict, optional): Custom thresholds to override default configuration.

    Returns:
        str: Expansion feasibility rating ("Expandable", "Limited Expansion", "Not Expandable").
    """
    config = custom_config or EXPANSION_THRESHOLDS
    t_expand_land = config.get("expandable_land", 5000.0)
    t_limit_land = config.get("limited_land", 1000.0)
    t_env_high = config.get("min_environmental_score", 80.0)
    t_inf_high = config.get("min_infrastructure_score", 70.0)
    t_env_mid = config.get("limited_environmental_score", 50.0)
    t_inf_mid = config.get("limited_infrastructure_score", 50.0)

    # 1. Check for Not Expandable constraints
    if (
        remaining_land < t_limit_land or 
        environmental_score < t_env_mid or 
        infrastructure_score < t_inf_mid
    ):
        return "Not Expandable"

    # 2. Check for Expandable constraints
    elif (
        remaining_land >= t_expand_land and 
        environmental_score >= t_env_high and 
        infrastructure_score >= t_inf_high
    ):
        return "Expandable"

    # 3. Fallback to Limited Expansion
    else:
        return "Limited Expansion"
