from app.services.wind_assessment import calculate_wind_class, classify_wind_site


def _classify_solar_resource(solar_irradiance: float) -> str:
    """
    Private helper to classify solar irradiance into Poor, Moderate, Good, or Excellent.

    Args:
        solar_irradiance (float): Solar irradiance in kWh/m²/day.

    Returns:
        str: Solar classification string.
    """
    if solar_irradiance < 3.0:
        return "Poor"
    elif 3.0 <= solar_irradiance < 4.5:
        return "Moderate"
    elif 4.5 <= solar_irradiance < 5.5:
        return "Good"
    else:
        return "Excellent"


def generate_reason(solar_class: str, wind_class: str, recommendation: str) -> str:
    """
    Formulate a human-readable reason describing the recommendation based on classes.

    Args:
        solar_class (str): Solar irradiance classification.
        wind_class (str): Wind speed classification.
        recommendation (str): Final deployment recommendation.

    Returns:
        str: Human-readable explanation.
    """
    if recommendation == "Hybrid":
        return "High solar irradiance and consistently strong wind resource."
    elif recommendation == "Solar":
        return f"Solar potential is {solar_class.lower()} while wind resource is {wind_class.lower()}."
    elif recommendation == "Wind":
        return f"Wind resource is {wind_class.lower()} while solar potential is {solar_class.lower()}."
    else:
        return "Neither solar nor wind resource meets the minimum deployment criteria."


def confidence_score(
    solar_irradiance: float,
    wind_speed: float,
    recommendation: str
) -> int:
    """
    Calculate a rule-based confidence percentage for the recommendation.

    Args:
        solar_irradiance (float): Solar irradiance in kWh/m²/day.
        wind_speed (float): Wind speed in m/s.
        recommendation (str): Recommended deployment strategy.

    Returns:
        int: Confidence percentage score between 0 and 100.
    """
    if recommendation == "Hybrid":
        # Base confidence for hybrid
        base = 80
        # Add points for exceptionally high values
        bonus_solar = min(10, int((solar_irradiance - 4.5) * 10)) if solar_irradiance > 4.5 else 0
        bonus_wind = min(10, int((wind_speed - 5.0) * 10)) if wind_speed > 5.0 else 0
        return min(100, base + bonus_solar + bonus_wind)

    elif recommendation == "Solar":
        base = 85
        bonus = min(15, int((solar_irradiance - 4.5) * 10)) if solar_irradiance > 4.5 else 0
        # Reduce confidence slightly if wind is moderate instead of poor
        penalty = 5 if wind_speed >= 3.0 else 0
        return max(50, min(100, base + bonus - penalty))

    elif recommendation == "Wind":
        base = 85
        bonus = min(15, int((wind_speed - 5.0) * 10)) if wind_speed > 5.0 else 0
        penalty = 5 if solar_irradiance >= 3.0 else 0
        return max(50, min(100, base + bonus - penalty))

    else:
        return 95  # High confidence when rejecting deployment suitability


def recommend_deployment(solar_irradiance: float, wind_speed: float) -> dict:
    """
    Orchestrate the classification, confidence scoring, and reasoning.

    Args:
        solar_irradiance (float): Solar irradiance in kWh/m²/day.
        wind_speed (float): Wind speed in m/s.

    Returns:
        dict: Recommendation profile dictionary containing deployment, confidence, and reason.
    """
    solar_class = _classify_solar_resource(solar_irradiance)
    wind_class = calculate_wind_class(wind_speed)

    recommendation = classify_wind_site(solar_class, wind_class)
    score = confidence_score(solar_irradiance, wind_speed, recommendation)
    reason = generate_reason(solar_class, wind_class, recommendation)

    return {
        "deployment": recommendation,
        "confidence": score,
        "reason": reason
    }
