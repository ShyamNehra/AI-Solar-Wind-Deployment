"""
Deployment Recommendation Module

Decides whether a location is best suited for Solar, Wind, or Hybrid deployment.
Integrates trained Machine Learning inference model with rule-based fallback logic.
"""

from typing import Optional, Dict, Any


def recommend_deployment(
    solar_class: str,
    wind_class: str
) -> str:
    """
    Rule-based baseline strategy recommendation.
    """
    if solar_class == "Excellent" and wind_class == "Excellent":
        return "Hybrid"

    if solar_class == "Excellent":
        return "Solar"

    if wind_class == "Excellent":
        return "Wind"

    if solar_class == "Good" and wind_class == "Good":
        return "Hybrid"

    if solar_class == "Good":
        return "Solar"

    if wind_class == "Good":
        return "Wind"

    return "Not Recommended"


def generate_reason(
    solar_class: str,
    wind_class: str
) -> str:
    """
    Explain recommendation.
    """
    deployment = recommend_deployment(solar_class, wind_class)
    reasons = {
        "Solar": "Solar irradiance is significantly stronger than wind resource.",
        "Wind": "Wind resource is stronger than available solar potential.",
        "Hybrid": "High solar irradiance and consistently strong wind resource.",
        "Not Recommended": "Neither solar nor wind resource is sufficient for deployment."
    }
    return reasons.get(deployment, "Resource potential evaluated for deployment.")


def confidence_score(
    solar_class: str,
    wind_class: str
) -> int:
    """
    Estimate recommendation confidence.
    """
    if solar_class == "Excellent" and wind_class == "Excellent":
        return 91
    if solar_class == "Excellent":
        return 88
    if wind_class == "Excellent":
        return 87
    if solar_class == "Good" or wind_class == "Good":
        return 75
    return 55


def recommend_strategy(
    solar_suitability: str,
    wind_suitability: str,
    solar_irradiance: Optional[float] = None,
    wind_speed: Optional[float] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    extra_features: Optional[Dict[str, Any]] = None
) -> dict:
    """
    Produce deployment recommendation integrating ML model predictions with rule-based fallbacks.
    """
    def map_to_class(suitability: str) -> str:
        if suitability == "Excellent":
            return "Excellent"
        if suitability in ["Highly Suitable", "Moderately Suitable", "Good"]:
            return "Good"
        return "Poor"

    s_class = map_to_class(solar_suitability)
    w_class = map_to_class(wind_suitability)

    # 1. Fallback Rule-Based Result
    rule_dep = recommend_deployment(s_class, w_class)
    rule_conf = confidence_score(s_class, w_class)
    rule_reason = generate_reason(s_class, w_class)

    ml_prediction_data = None

    # 2. Try ML Model Inference Engine
    try:
        from app.ml.inference import ModelInferenceModule
        inference_module = ModelInferenceModule()

        # Deduce numeric values if not passed
        s_val = solar_irradiance if solar_irradiance is not None else (6.5 if s_class == "Excellent" else 5.2 if s_class == "Good" else 3.5)
        w_val = wind_speed if wind_speed is not None else (9.0 if w_class == "Excellent" else 6.5 if w_class == "Good" else 4.0)

        ml_res = inference_module.predict_deployment_strategy(
            solar_irradiance=s_val,
            wind_speed=w_val,
            latitude=latitude,
            longitude=longitude,
            extra_features=extra_features
        )

        dep = ml_res["deployment"]
        conf = ml_res["confidence"]
        reason = ml_res["reason"]
        ml_prediction_data = ml_res.get("ml_prediction")

    except Exception as e:
        dep = rule_dep
        conf = rule_conf
        reason = rule_reason

    return {
        "deployment": dep,
        "confidence": conf,
        "reason": reason,
        "ml_prediction": ml_prediction_data
    }