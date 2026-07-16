from app.evaluation.weights import DEFAULT_WEIGHTS

def normalize_value(value: float, min_val: float, max_val: float, invert: bool = False) -> float:
    """Helper to convert any raw feature into a standardized 0-100 score."""
    if max_val == min_val:
        return 100.0
    
    normalized = (value - min_val) / (max_val - min_val) * 100.0
    normalized = max(0.0, min(100.0, normalized))  # Clamp between 0 and 100
    
    return 100.0 - normalized if invert else normalized

def calculate_suitability_score(features: dict, weights: dict = DEFAULT_WEIGHTS) -> float:
    """
    Computes a weighted suitability index (0.0 to 100.0) from raw site features.
    """
    # Normalize features to a 0-100 scale (Inverting distances: smaller distance = better score)
    scores = {
        "solar_irradiance": normalize_value(features.get("solar_irradiance", 0.0), 2.0, 7.0),
        "wind_speed": normalize_value(features.get("wind_speed", 0.0), 2.0, 12.0),
        "slope": normalize_value(features.get("slope", 0.0), 0.0, 20.0, invert=True),
        "grid_distance": normalize_value(features.get("grid_distance", 0.0), 100.0, 50000.0, invert=True),
        "road_distance": normalize_value(features.get("road_distance", 0.0), 50.0, 15000.0, invert=True)
    }

    # Apply weights
    weighted_score = sum(scores[key] * weights[key] for key in weights)
    return round(weighted_score, 2)