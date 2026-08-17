from app.evaluation.constraints import (
    check_slope,
    check_solar_irradiance,
    check_wind_speed,
    check_grid_distance,
    check_road_distance,
)

from app.evaluation.scorer import SiteScorer
from app.evaluation.recommendation import get_recommendation


def evaluate_site(site_id: int, features: dict) -> dict:
    """
    Evaluate a site using constraints,
    scoring and recommendation.
    """

    # -----------------------------
    # Constraint Checks
    # -----------------------------

    slope_ok = check_slope(features["slope"])
    solar_ok = check_solar_irradiance(features["solar_irradiance"])
    wind_ok = check_wind_speed(features["wind_speed"])
    grid_ok = check_grid_distance(features["distance_to_grid"])
    road_ok = check_road_distance(features["distance_to_road"])

    # -----------------------------
    # Site Scoring
    # -----------------------------

    scorer = SiteScorer()

    score_result = scorer.calculate_overall_score(
        solar_irradiance=features["solar_irradiance"],
        wind_speed=features["wind_speed"],
        slope=features["slope"],
        elevation=features["elevation"],
        grid_distance=features["distance_to_grid"],
        road_distance=features["distance_to_road"],
    )

    overall_score = score_result["overall_site_score"]

    # -----------------------------
    # Recommendation
    # -----------------------------

    recommendation = get_recommendation(overall_score)

    # -----------------------------
    # Failed Constraints
    # -----------------------------

    failed = []

    if not slope_ok:
        failed.append("Slope exceeds maximum limit.")

    if not solar_ok:
        failed.append("Solar irradiance is below threshold.")

    if not wind_ok:
        failed.append("Wind speed is below threshold.")

    if not grid_ok:
        failed.append("Distance to grid is too large.")

    if not road_ok:
        failed.append("Distance to road is too large.")

    # -----------------------------
    # Final Report
    # -----------------------------

    report = {

        "site_id": site_id,

        "latitude": features["latitude"],
        "longitude": features["longitude"],

        "overall_score": overall_score,

        "recommendation": recommendation,

        "category_scores": score_result,

        "criteria_evaluation": {

            "solar_irradiance": {
                "value": features["solar_irradiance"],
                "status": "Pass" if solar_ok else "Fail"
            },

            "wind_speed": {
                "value": features["wind_speed"],
                "status": "Pass" if wind_ok else "Fail"
            },

            "slope": {
                "value": features["slope"],
                "status": "Pass" if slope_ok else "Fail"
            },

            "distance_to_grid": {
                "value": features["distance_to_grid"],
                "status": "Pass" if grid_ok else "Fail"
            },

            "distance_to_road": {
                "value": features["distance_to_road"],
                "status": "Pass" if road_ok else "Fail"
            }

        },

        "constraints": {

            "all_constraints_passed": (
                slope_ok
                and solar_ok
                and wind_ok
                and grid_ok
                and road_ok
            )

        },

        "remarks": (
            ["All constraints satisfied."]
            if len(failed) == 0
            else failed
        )

    }

    return report