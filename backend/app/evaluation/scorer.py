from app.evaluation.category_scoring import CategoryScoring
from app.evaluation.weights import (
    RENEWABLE_WEIGHT,
    TERRAIN_WEIGHT,
    INFRASTRUCTURE_WEIGHT,
    ENVIRONMENTAL_WEIGHT,
    ECONOMIC_WEIGHT,
)


class SiteScorer:
    """
    Calculate the Overall Site Suitability Score.
    """

    def __init__(self):
        self.category = CategoryScoring()

    def calculate_overall_score(
        self,
        solar_irradiance,
        wind_speed,
        slope,
        elevation,
        grid_distance,
        road_distance,
    ):

        renewable = self.category.renewable_resource_score(
            solar_irradiance,
            wind_speed,
        )

        terrain = self.category.terrain_score(
            slope,
            elevation,
        )

        infrastructure = self.category.infrastructure_score(
            grid_distance,
            road_distance,
        )

        environmental = self.category.environmental_score()

        economic = self.category.economic_score()

        overall_score = (
            renewable * RENEWABLE_WEIGHT
            + terrain * TERRAIN_WEIGHT
            + infrastructure * INFRASTRUCTURE_WEIGHT
            + environmental * ENVIRONMENTAL_WEIGHT
            + economic * ECONOMIC_WEIGHT
        )

        return {
            "renewable_resource_score": round(renewable, 2),
            "terrain_score": round(terrain, 2),
            "infrastructure_score": round(infrastructure, 2),
            "environmental_score": round(environmental, 2),
            "economic_score": round(economic, 2),
            "overall_site_score": round(overall_score, 2),
        }


# --------------------------------------------------------------------
# This function is required by evaluator.py
# --------------------------------------------------------------------
def calculate_score(features: dict):
    scorer = SiteScorer()

    scores = scorer.calculate_overall_score(
        solar_irradiance=features["solar_irradiance"],
        wind_speed=features["wind_speed"],
        slope=features["slope"],
        elevation=features["elevation"],
        grid_distance=features["distance_to_grid"],
        road_distance=features["distance_to_road"],
    )

    return scores["overall_site_score"]