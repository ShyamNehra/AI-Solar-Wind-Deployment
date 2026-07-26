from typing import Dict, Any


def classify_solar_site(solar_irradiance: float) -> str:
    """
    Helper function to classify solar irradiance (kWh/m2/day).
    """
    if solar_irradiance < 3.5:
        return "Poor"
    elif 3.5 <= solar_irradiance < 5.0:
        return "Moderate"
    elif 5.0 <= solar_irradiance <= 6.0:
        return "Good"
    else:  # > 6.0 kWh/m2/day
        return "Excellent"


def generate_reason(solar_tier: str, wind_tier: str, deployment: str) -> str:
    """
    Task 5: Generates human-readable explanation for the recommendation.
    """
    if deployment == "Hybrid":
        return f"High solar irradiance ({solar_tier.lower()}) and consistently strong wind resource ({wind_tier.lower()})."
    elif deployment == "Solar":
        return f"Strong solar potential ({solar_tier.lower()}) combined with suboptimal wind conditions ({wind_tier.lower()})."
    elif deployment == "Wind":
        return f"Strong wind resource ({wind_tier.lower()}) combined with lower solar potential ({solar_tier.lower()})."
    else:
        return f"Both solar ({solar_tier.lower()}) and wind ({wind_tier.lower()}) resources are insufficient for commercial deployment."


def confidence_score(solar_irradiance: float, wind_speed: float, deployment: str) -> int:
    """
    Task 5: Calculates a confidence score (0-100) based on resource abundance.
    """
    # Normalize solar (range 0 to 7) and wind (range 0 to 12)
    solar_norm = min(solar_irradiance / 7.0, 1.0)
    wind_norm = min(wind_speed / 12.0, 1.0)

    if deployment == "Hybrid":
        score = ((solar_norm + wind_norm) / 2.0) * 100
    elif deployment == "Solar":
        score = solar_norm * 100
    elif deployment == "Wind":
        score = wind_norm * 100
    else:
        score = 50.0

    return int(round(score))


def recommend_deployment(solar_irradiance: float, wind_speed: float, wind_tier_input: str = None) -> Dict[str, Any]:
    """
    Task 4 & 5: Core Decision Matrix for Deployment Recommendation.
    """
    solar_tier = classify_solar_site(solar_irradiance)
    
    # Import or use local wind classifier
    from app.services.wind_assessment import classify_wind_site
    wind_tier = wind_tier_input or classify_wind_site(wind_speed)

    # Task 4 Decision Logic Matrix
    if solar_tier in ["Good", "Excellent"] and wind_tier in ["Good", "Excellent"]:
        deployment = "Hybrid"
    elif solar_tier in ["Good", "Excellent"] and wind_tier in ["Poor", "Moderate"]:
        deployment = "Solar"
    elif solar_tier in ["Poor", "Moderate"] and wind_tier in ["Good", "Excellent"]:
        deployment = "Wind"
    else:
        # Default to whichever resource is stronger if both are moderate/poor
        deployment = "Solar" if solar_irradiance >= 4.0 else "Unsuitable"

    reason = generate_reason(solar_tier, wind_tier, deployment)
    confidence = confidence_score(solar_irradiance, wind_speed, deployment)

    return {
        "deployment": deployment,
        "confidence": confidence,
        "reason": reason
    }