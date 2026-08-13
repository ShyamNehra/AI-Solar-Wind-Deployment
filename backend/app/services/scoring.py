def normalize_min_max(val, min_val, max_val, invert=False):
    if val is None:
        return 0.0
    # Bound input
    val = max(min(val, max_val), min_val)
    if max_val == min_val:
        return 100.0
    
    score = ((val - min_val) / (max_val - min_val)) * 100.0
    if invert:
        return 100.0 - score
    return score

def calculate_category_scores(solar_irr, wind_speed, slope, elevation, dist_grid, dist_road):
    """
    Normalizes inputs to a 0-100 scale and computes category-wise scores.
    """
    # 1. Resource scores
    # Solar: typical GHI ranges from 2.0 to 8.0 kWh/m2/day
    solar_score = normalize_min_max(solar_irr, 2.0, 8.0)
    # Wind: typical wind speed ranges from 2.0 to 18.0 m/s
    wind_score = normalize_min_max(wind_speed, 2.0, 18.0)
    resource_score = (solar_score * 0.5) + (wind_score * 0.5)

    # 2. Terrain scores
    # Slope: lower is better for solar/wind farms (0 to 30 degrees)
    slope_score = normalize_min_max(slope, 0.0, 20.0, invert=True)
    # Elevation: higher typical elevations (e.g. up to 1500m) can be suitable but flat is preferred. We scale 0-1500m.
    elevation_score = normalize_min_max(elevation, 0.0, 1500.0, invert=False)
    terrain_score = (slope_score * 0.7) + (elevation_score * 0.3)

    # 3. Infrastructure accessibility
    # Grid distance: 0m to 10000m. Lower is better.
    grid_score = normalize_min_max(dist_grid, 0.0, 10000.0, invert=True)
    # Road distance: 0m to 5000m. Lower is better.
    road_score = normalize_min_max(dist_road, 0.0, 5000.0, invert=True)
    infra_score = (grid_score * 0.6) + (road_score * 0.4)

    return {
        "renewable_resource_score": round(resource_score, 2),
        "terrain_score": round(terrain_score, 2),
        "infrastructure_score": round(infra_score, 2),
        "environmental_score": round(normalize_min_max(slope, 0.0, 15.0, invert=True), 2),
        "economic_score": round((infra_score * 0.5) + (resource_score * 0.5), 2)
    }

def calculate_overall_score(category_scores, weights=None):
    """
    Aggregates category scores into a single weighted overall score.
    """
    if weights is None:
        weights = {
            "renewable_resource_score": 0.40,
            "terrain_score": 0.30,
            "infrastructure_score": 0.20,
            "environmental_score": 0.05,
            "economic_score": 0.05
        }
    
    overall = sum(category_scores[cat] * weight for cat, weight in weights.items())
    return round(overall, 2)
