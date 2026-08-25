def validate_feasibility(slope, elevation, dist_grid, dist_road):
    """
    Validates hard constraints and returns technical feasibility state.
    """
    hard_failed = []
    
    # Hard constraint: slope must be less than 20 degrees
    if slope >= 20.0:
        hard_failed.append(f"Slope exceeds limit: {slope}° >= 20°")
    
    # Hard constraint: elevation must be less than 2000m
    if elevation >= 2000.0:
        hard_failed.append(f"Elevation exceeds limit: {elevation}m >= 2000m")

    # Hard constraint: distance to grid must be less than 15000m (extreme exclusion)
    if dist_grid >= 15000.0:
        hard_failed.append(f"Grid distance too far: {dist_grid}m >= 15000m")

    is_feasible = len(hard_failed) == 0
    
    return {
        "technical_feasibility": is_feasible,
        "hard_failed_constraints": hard_failed,
        "soft_feasibility_score": round(100.0 - (min(dist_grid, 10000.0)/100.0 * 0.6 + min(dist_road, 5000.0)/50.0 * 0.4), 2)
    }

def determine_deployment_strategy(solar_score, wind_score):
    """
    Determines whether Solar, Wind, or Hybrid deployment is recommended.
    """
    if solar_score >= 50.0 and wind_score >= 50.0:
        return "Hybrid"
    elif solar_score > wind_score:
        return "Solar"
    elif wind_score > solar_score:
        return "Wind"
    else:
        return "Solar" # Default fallback

def plan_capacity(strategy, area_sq_m):
    """
    Estimates capacity based on available area and technology type.
    """
    # Guidelines: Solar requires ~10,000 sq m per MW. Wind requires ~20,000 sq m per MW.
    if strategy == "Solar":
        capacity_mw = area_sq_m / 10000.0
    elif strategy == "Wind":
        capacity_mw = area_sq_m / 20000.0
    elif strategy == "Hybrid":
        # Hybrid sharing area (50/50 allocation)
        capacity_mw = (area_sq_m * 0.5 / 10000.0) + (area_sq_m * 0.5 / 20000.0)
    else:
        capacity_mw = 0.0
    
    return round(max(capacity_mw, 0.1), 2)

def analyze_expansion_feasibility(area_sq_m):
    """
    Evaluates potential for expansion.
    """
    if area_sq_m > 100000.0:
        return "Expandable"
    elif area_sq_m >= 40000.0:
        return "Limited Expansion"
    else:
        return "Not Expandable"

def generate_deployment_plan(slope, elevation, dist_grid, dist_road, area_sq_m, solar_score, wind_score):
    feasibility = validate_feasibility(slope, elevation, dist_grid, dist_road)
    
    if not feasibility["technical_feasibility"]:
        return {
            "recommended_technology": "None",
            "recommended_capacity_mw": 0.0,
            "expansion_status": "Not Expandable",
            "technical_feasibility": False,
            "remarks": f"Site rejected due to hard constraint violations: {', '.join(feasibility['hard_failed_constraints'])}"
        }
        
    strategy = determine_deployment_strategy(solar_score, wind_score)
    capacity = plan_capacity(strategy, area_sq_m)
    expansion = analyze_expansion_feasibility(area_sq_m)
    
    return {
        "recommended_technology": strategy,
        "recommended_capacity_mw": capacity,
        "expansion_status": expansion,
        "technical_feasibility": True,
        "remarks": f"Site is highly suitable for {strategy} deployment. Expansion profile is {expansion}."
    }
