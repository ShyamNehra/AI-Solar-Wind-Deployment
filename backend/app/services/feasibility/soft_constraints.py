"""
Soft Constraint Scoring Module.
Evaluates non-mandatory engineering factors, assigns tiered distance & physical scores,
and calculates composite weighted Feasibility Score (0-100) and Rating Classification.
"""

from typing import Dict, Any, Tuple


class SoftConstraintScorer:
    """
    Evaluates soft engineering constraints:
    - Road Distance
    - Grid / Substation Distance
    - Accessibility
    - Terrain Score
    - Infrastructure Availability
    - Environmental Risk Score

    Weights:
    - Infrastructure: 30%
    - Accessibility: 20%
    - Terrain: 20%
    - Grid Access: 20%
    - Environmental Risk: 10%
    """

    @staticmethod
    def score_distance_km(distance_km: float) -> float:
        """
        Tiered scoring for road and grid distance:
        0 - 5 km  -> 100
        5 - 10 km -> 80
        10 - 20 km -> 60
        > 20 km    -> 30
        """
        dist = float(distance_km) if distance_km is not None else 5.0
        if dist <= 5.0:
            return 100.0
        elif dist <= 10.0:
            return 80.0
        elif dist <= 20.0:
            return 60.0
        else:
            return 30.0

    def evaluate(self, features: Dict[str, Any]) -> Tuple[float, str, Dict[str, float]]:
        """
        Evaluates soft constraints and calculates overall feasibility score & classification rating.
        Returns Tuple of (feasibility_score, rating_string, soft_scores_dict).
        """
        # 1. Road Distance Score
        road_dist = float(features.get("road_distance", 4.0) or 4.0)
        road_score = self.score_distance_km(road_dist)

        # 2. Grid / Substation Distance Score
        substation_dist = float(features.get("substation_distance", 8.0) or 8.0)
        grid_dist = float(features.get("grid_distance", substation_dist) or substation_dist)
        grid_score = self.score_distance_km(grid_dist)

        # 3. Accessibility Score
        if "accessibility" in features and features["accessibility"] is not None:
            access_score = float(features["accessibility"])
        else:
            # Derived accessibility from road distance
            access_score = max(0.0, min(100.0, 100.0 - (road_dist * 3.5)))

        # 4. Terrain Score
        if "terrain_score" in features and features["terrain_score"] is not None:
            terrain_score = float(features["terrain_score"])
        else:
            slope = float(features.get("slope", 2.0) or 2.0)
            elevation = float(features.get("elevation", 250.0) or 250.0)
            terrain_score = max(0.0, min(100.0, 100.0 - (slope * 3.0) - (elevation / 100.0)))

        # 5. Infrastructure Availability Score
        if "infrastructure_score" in features and features["infrastructure_score"] is not None:
            infra_score = float(features["infrastructure_score"])
        else:
            infra_score = round((road_score * 0.5) + (grid_score * 0.5), 1)

        # 6. Environmental Risk Score (100 = low risk, 0 = high risk)
        if "environmental_score" in features and features["environmental_score"] is not None:
            env_risk_score = float(features["environmental_score"])
        elif "environmental_risk" in features and features["environmental_risk"] is not None:
            env_risk_score = float(features["environmental_risk"])
        else:
            env_risk_score = 85.0

        # Weighted Score Calculation
        weighted_score = (
            (infra_score * 0.30) +
            (access_score * 0.20) +
            (terrain_score * 0.20) +
            (grid_score * 0.20) +
            (env_risk_score * 0.10)
        )
        feasibility_score = round(max(0.0, min(100.0, weighted_score)), 1)

        # Classification Rating
        if feasibility_score >= 90.0:
            rating = "Excellent"
        elif feasibility_score >= 75.0:
            rating = "Good"
        elif feasibility_score >= 60.0:
            rating = "Moderate"
        else:
            rating = "Poor"

        soft_scores_dict = {
            "road_distance": road_score,
            "grid_access": grid_score,
            "accessibility": round(access_score, 1),
            "terrain": round(terrain_score, 1),
            "infrastructure": round(infra_score, 1),
            "environmental_risk": round(env_risk_score, 1),
        }

        return feasibility_score, rating, soft_scores_dict
