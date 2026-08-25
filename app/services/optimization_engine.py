from app.services.deployment_strategy import recommend_deployment


def optimize_deployment_strategy(
    solar_irradiance: float,
    wind_speed: float
) -> dict:
    """
    Determine the optimized deployment strategy based on solar and wind resource inputs.
    Reuses recommend_deployment() to determine the technology recommendation.

    Args:
        solar_irradiance (float): Solar irradiance in kWh/m²/day.
        wind_speed (float): Wind speed in m/s.

    Returns:
        dict: Optimization profile containing optimized technology, confidence, and strategy remarks.
    """
    recommendation = recommend_deployment(solar_irradiance, wind_speed)

    deployment_type = recommendation.get("deployment", "None")
    confidence = recommendation.get("confidence", 0)
    reason = recommendation.get("reason", "")

    # Formulate optimization remarks based on recommendation outputs
    if deployment_type == "Hybrid":
        remarks = "Hybrid deployment is optimized due to high concurrent solar and wind potentials."
    elif deployment_type == "Solar":
        remarks = "Solar-only deployment is optimized as solar resources significantly outperform wind."
    elif deployment_type == "Wind":
        remarks = "Wind-only deployment is optimized as wind speed profiles significantly outperform solar."
    else:
        remarks = "Site is not suitable for optimized commercial deployment under current resource conditions."

    return {
        "optimized_technology": deployment_type,
        "confidence": confidence,
        "strategy_remarks": remarks
    }
