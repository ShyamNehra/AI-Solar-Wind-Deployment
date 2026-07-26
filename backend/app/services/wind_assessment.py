# app/services/wind_assessment.py

def classify_wind_site(wind_speed: float) -> str:
    """
    Task 2: Classifies wind speed into site quality tiers.
    """
    if wind_speed < 3.0:
        return "Poor"
    elif 3.0 <= wind_speed < 5.0:
        return "Moderate"
    elif 5.0 <= wind_speed <= 7.0:
        return "Good"
    else:  # > 7.0 m/s
        return "Excellent"


def calculate_capacity_factor(wind_speed: float) -> float:
    """
    Task 3: Estimates wind capacity factor based on wind speed tiers.
    """
    if wind_speed < 3.0:
        return 0.10  # 10% (Very low efficiency / below cut-in)
    elif 3.0 <= wind_speed < 5.0:
        return 0.22  # 22%
    elif 5.0 <= wind_speed <= 7.0:
        return 0.32  # 32%
    else:  # > 7.0 m/s
        return 0.42  # 42% (High performance offshore/onshore target)


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