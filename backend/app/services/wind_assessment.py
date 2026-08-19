# app/services/wind_assessment.py

def classify_wind_site(wind_speed: float) -> str:
    """
    Classifies annual average wind speed at hub height into quality tiers.
    Benchmark: > 5.8 m/s annual average speed at hub height is Good for commercial wind power plants.
    """
    if wind_speed < 3.5:
        return "Poor"
    elif 3.5 <= wind_speed < 5.8:
        return "Moderate"
    elif 5.8 <= wind_speed <= 7.5:
        return "Good"
    else:  # > 7.5 m/s
        return "Excellent"


def calculate_capacity_factor(wind_speed: float) -> float:
    """
    Estimates wind capacity factor based on wind speed tiers.
    """
    if wind_speed < 3.5:
        return 0.10  # Below cut-in / minimal yield
    elif 3.5 <= wind_speed < 5.8:
        return 0.22  # Moderate performance
    elif 5.8 <= wind_speed <= 7.5:
        return 0.35  # Good commercial onshore performance
    else:  # > 7.5 m/s
        return 0.44  # High performance target


def calculate_wind_class(wind_speed: float) -> dict:
    """
    Task 1: Orchestrates wind classification and capacity factor estimation.
    """
    classification = classify_wind_site(wind_speed)
    cf = calculate_capacity_factor(wind_speed)
    
    return {
        "wind_speed_ms": wind_speed,
        "wind_class": classification,
        "estimated_capacity_factor": cf
    }