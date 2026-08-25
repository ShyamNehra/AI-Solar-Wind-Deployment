def calculate_weighted_score(
    resource_score: float,
    geographic_score: float,
    infrastructure_score: float,
    environmental_score: float,
    economic_score: float
) -> float:
    """
    Calculate the overall deployment suitability score using the locked weighted formula:
    Renewable Resource Availability: 35%
    Geographic Suitability: 25%
    Infrastructure Accessibility: 15%
    Environmental Impact: 15%
    Economic Feasibility: 10%
    """
    score = (
        (resource_score * 0.35) +
        (geographic_score * 0.25) +
        (infrastructure_score * 0.15) +
        (environmental_score * 0.15) +
        (economic_score * 0.10)
    )
    return round(score, 2)

def calculate_hybrid_score(solar_score: float, wind_score: float) -> float:
    """
    Genuinely combine solar and wind scores into a single overall hybrid score
    using an equal-weighted co-location deployment model (50% solar, 50% wind).
    """
    return round((solar_score * 0.5) + (wind_score * 0.5), 2)

def map_score_to_category(score: float) -> str:
    """
    Map deployment score to the 5 suitability categories based on the Phase 0 score bands:
    - Excellent: 85.0 - 100.0
    - Highly Suitable: 70.0 - 84.9
    - Moderately Suitable: 50.0 - 69.9
    - Low Suitability: 30.0 - 49.9
    - Unsuitable: 0.0 - 29.9
    """
    if score >= 85.0:
        return "Excellent"
    elif score >= 70.0:
        return "Highly Suitable"
    elif score >= 50.0:
        return "Moderately Suitable"
    elif score >= 30.0:
        return "Low Suitability"
    else:
        return "Unsuitable"
