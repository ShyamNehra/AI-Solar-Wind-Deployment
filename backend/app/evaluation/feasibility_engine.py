# app/evaluation/feasibility_engine.py
from typing import Dict, Any, List, Tuple


class FeasibilityEngine:
    """
    Dedicated engineering evaluation engine that validates site hard constraints
    and calculates soft constraint feasibility scores.
    """

    # Hard Constraint Thresholds
    MAX_SLOPE_DEGREES = 15.0  # Excessive slope makes installation unsafe/unviable
    RESTRICTED_LAND_TYPES = {"protected_forest", "wetland", "urban_residential", "military_zone"}
    MIN_IRRADIANCE = 2.5      # Minimum viable solar irradiance (kWh/m²/day)
    MIN_WIND_SPEED = 3.0      # Minimum viable wind speed (m/s)

    def evaluate_hard_constraints(self, env_features: Dict[str, Any], deployment_type: str) -> Tuple[bool, List[str]]:
        """
        Task 2: Hard Constraint Validation.
        Fails immediately if mandatory constraints are violated.
        """
        violations = []
        
        # 1. Slope / Terrain Check
        slope = env_features.get("slope", 0.0)
        if slope > self.MAX_SLOPE_DEGREES:
            violations.append(f"Unacceptable terrain slope: {slope}° exceeds maximum limit of {self.MAX_SLOPE_DEGREES}°")

        # 2. Restricted Land Use Check
        land_use = str(env_features.get("land_use_type", "unrestricted")).lower()
        if land_use in self.RESTRICTED_LAND_TYPES:
            violations.append(f"Restricted land use zone: '{land_use}' prohibits renewable deployment")

        # 3. Minimum Resource Viability Check
        dtype = deployment_type.lower()
        if dtype == "solar":
            irradiance = env_features.get("solar_irradiance", 0.0)
            if irradiance < self.MIN_IRRADIANCE:
                violations.append(f"Insufficient solar irradiance: {irradiance} kWh/m²/day is below cutoff ({self.MIN_IRRADIANCE})")
        elif dtype == "wind":
            wind = env_features.get("wind_speed", 0.0)
            if wind < self.MIN_WIND_SPEED:
                violations.append(f"Insufficient wind speed: {wind} m/s is below cutoff ({self.MIN_WIND_SPEED})")

        is_feasible = len(violations) == 0
        return is_feasible, violations

    def evaluate_soft_constraints(self, env_features: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
        """
        Task 3: Soft Constraint Scoring (0 to 100 Scale).
        Evaluates proximity to infrastructure and accessibility without outright rejection.
        """
        scores = {}

        # 1. Proximity to Power Grid (0-40 pts)
        grid_dist_km = env_features.get("distance_to_grid_km", 10.0)
        if grid_dist_km <= 5.0:
            scores["grid_proximity"] = 40.0
        elif grid_dist_km <= 20.0:
            scores["grid_proximity"] = round(40.0 * (1 - (grid_dist_km - 5) / 15), 2)
        else:
            scores["grid_proximity"] = 5.0

        # 2. Road Accessibility (0-30 pts)
        road_dist_km = env_features.get("distance_to_road_km", 2.0)
        if road_dist_km <= 2.0:
            scores["accessibility"] = 30.0
        elif road_dist_km <= 10.0:
            scores["accessibility"] = round(30.0 * (1 - (road_dist_km - 2) / 8), 2)
        else:
            scores["accessibility"] = 5.0

        # 3. Terrain Soft Penalty (0-30 pts)
        slope = env_features.get("slope", 0.0)
        if slope <= 5.0:
            scores["terrain_usability"] = 30.0
        else:
            # Gradually penalize slope up to hard constraint threshold (15°)
            scores["terrain_usability"] = max(0.0, round(30.0 * (1 - (slope - 5) / 10), 2))

        total_score = round(sum(scores.values()), 2)
        return total_score, scores

    def run_assessment(self, env_features: Dict[str, Any], deployment_type: str) -> Dict[str, Any]:
        """Runs full feasibility pass combining hard and soft checks."""
        is_feasible, hard_violations = self.evaluate_hard_constraints(env_features, deployment_type)
        soft_score, soft_breakdown = self.evaluate_soft_constraints(env_features)

        # Final recommendation logic combining ML feasibility
        if not is_feasible:
            final_status = "REJECTED"
            recommendation = "Site technically unfeasible due to mandatory constraint violations."
            effective_score = 0.0
        elif soft_score >= 70.0:
            final_status = "APPROVED"
            recommendation = "High feasibility site. Recommended for immediate deployment investment."
            effective_score = soft_score
        else:
            final_status = "CONDITIONAL"
            recommendation = "Site feasible but requires infrastructure investment (e.g. grid connection / road access)."
            effective_score = soft_score

        return {
            "is_technically_feasible": is_feasible,
            "final_status": final_status,
            "feasibility_score": effective_score,
            "recommendation": recommendation,
            "constraint_summary": {
                "hard_constraint_violations": hard_violations,
                "soft_score_breakdown": soft_breakdown
            }
        }