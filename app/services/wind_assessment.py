def calculate_wind_class(wind_speed: float) -> str:
    """
    Classify wind speed into wind classes: Poor, Moderate, Good, or Excellent.

    Args:
        wind_speed (float): Wind speed in m/s.

    Returns:
        str: Wind classification string.
    """
    if wind_speed < 3.0:
        return "Poor"
    elif 3.0 <= wind_speed < 5.0:
        return "Moderate"
    elif 5.0 <= wind_speed < 7.0:
        return "Good"
    else:
        return "Excellent"


def calculate_capacity_factor(wind_speed: float) -> float:
    """
    Estimate capacity factor based on wind speed ranges using deterministic rules.

    Args:
        wind_speed (float): Wind speed in m/s.

    Returns:
        float: Estimated capacity factor between 0.0 and 1.0.
    """
    if wind_speed < 3.0:
        return 0.0  # Below cut-in wind speed
    elif 3.0 <= wind_speed < 5.0:
        return 0.15
    elif 5.0 <= wind_speed < 7.0:
        return 0.30
    elif 7.0 <= wind_speed < 12.0:
        return 0.45
    else:
        return 0.50  # Rated speed / peak capacity factor


def classify_wind_site(solar_class: str, wind_class: str) -> str:
    """
    Determine the recommended deployment type based on solar and wind classes.

    Args:
        solar_class (str): Solar irradiance classification (Poor, Moderate, Good, Excellent).
        wind_class (str): Wind speed classification (Poor, Moderate, Good, Excellent).

    Returns:
        str: Site classification recommendation (Solar, Wind, Hybrid, or None).
    """
    # Mapping classifications to scores to enable clean comparison and modular logic
    class_scores = {
        "Poor": 1,
        "Moderate": 2,
        "Good": 3,
        "Excellent": 4
    }

    solar_score = class_scores.get(solar_class, 1)
    wind_score = class_scores.get(wind_class, 1)

    # Hybrid logic: Both solar and wind are strong (Good or Excellent)
    if solar_score >= 3 and wind_score >= 3:
        return "Hybrid"
    # Solar logic: Solar is strong, wind is weak
    elif solar_score >= 3 and wind_score < 3:
        return "Solar"
    # Wind logic: Wind is strong, solar is weak
    elif wind_score >= 3 and solar_score < 3:
        return "Wind"
    # Fallback: Neither are strong, check if moderate levels are present
    elif solar_score == 2 or wind_score == 2:
        # If one is moderate, recommend the stronger one
        if solar_score > wind_score:
            return "Solar"
        elif wind_score > solar_score:
            return "Wind"
        else:
            return "Solar"  # Default fallback if both are moderate
    else:
        return "None"
