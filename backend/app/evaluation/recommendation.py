def generate_recommendation(score: float, is_viable: bool) -> dict:
    """
    Converts a suitability index score into categorized deployment recommendations.
    """
    if not is_viable:
        return {
            "tier": "Not Recommended",
            "action_advice": "Site rejected due to critical boundary constraint violations.",
            "color_code": "#FF4D4D"
        }

    if score >= 85.0:
        return {
            "tier": "Highly Suitable",
            "action_advice": "Ideal conditions. Proceed immediately with land acquisition and technical feasibility designs.",
            "color_code": "#2ECC71"
        }
    elif 70.0 <= score < 85.0:
        return {
            "tier": "Suitable",
            "action_advice": "Feasible location. Recommended to optimize logistics and grid connection pricing.",
            "color_code": "#F1C40F"
        }
    elif 50.0 <= score < 70.0:
        return {
            "tier": "Moderately Suitable",
            "action_advice": "Marginal metrics. High civil engineering grading or grid connection costs expected.",
            "color_code": "#E67E22"
        }
    else:
        return {
            "tier": "Not Recommended",
            "action_advice": "Sub-optimal resource parameters. Site investment not economically viable.",
            "color_code": "#E74C3C"
        }