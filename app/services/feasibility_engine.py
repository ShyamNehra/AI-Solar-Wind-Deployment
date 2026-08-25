from app.services.scoring_engine import (
    normalize_distance_grid,
    normalize_distance_road,
    normalize_slope,
    calculate_environmental_score,
    calculate_economic_score
)

class TechnicalFeasibilityEngine:
    """
    Feasibility engine to validate mandatory engineering constraints
    and score soft constraints for site suitability.
    """

    def validate_hard_constraints(self, site_data: dict) -> list[str]:
        """
        Validate mandatory engineering constraints.
        Returns a list of violated constraint descriptions.
        """
        critical_violations = []

        slope = float(site_data.get("slope", 0.0))
        protected_area_dist = float(site_data.get("protected_area_distance", 10.0))
        elevation = float(site_data.get("elevation", 0.0))
        environmental_impact = float(site_data.get("environmental_impact_level", 0.0))

        if slope > 20.0:
            critical_violations.append("Slope Limit Exceeded: Slope must be <= 20 degrees.")
        if protected_area_dist < 2.0:
            critical_violations.append("Protected Area Proximity: Site must be >= 2km from protected areas.")
        if elevation > 3000.0:
            critical_violations.append("Elevation Limit Exceeded: Elevation must be <= 3000 meters.")
        if environmental_impact > 8.0:
            critical_violations.append("Environmental Impact Threshold: Impact level must be <= 8.0.")

        return critical_violations

    def calculate_soft_constraint_score(self, site_data: dict) -> float:
        """
        Calculate a soft feasibility score (0 to 100) based on accessibility,
        proximity, economic, and environmental factors.
        """
        grid_dist = float(site_data.get("distance_to_grid", 0.0))
        road_dist = float(site_data.get("distance_to_road", 0.0))
        slope = float(site_data.get("slope", 0.0))
        prot_dist = float(site_data.get("protected_area_distance", 10.0))
        env_impact = float(site_data.get("environmental_impact_level", 0.0))
        land_cost = float(site_data.get("land_cost_per_acre", 10000.0))
        conn_cost = float(site_data.get("grid_connection_cost", 50000.0))

        # Normalize factors using existing scoring engine functions to avoid code duplication
        grid_score = normalize_distance_grid(grid_dist)
        road_score = normalize_distance_road(road_dist)
        slope_score = normalize_slope(slope)
        env_score = calculate_environmental_score(prot_dist, env_impact)
        eco_score = calculate_economic_score(land_cost, conn_cost)

        # Weighted Soft Feasibility Score
        soft_score = (
            (grid_score * 0.25) +
            (road_score * 0.20) +
            (slope_score * 0.20) +
            (env_score * 0.20) +
            (eco_score * 0.15)
        )

        return round(soft_score, 2)

    def evaluate_site(self, site_data: dict) -> dict:
        """
        Evaluate hard and soft constraints.
        Returns a dictionary representing feasibility status and score.
        """
        critical_violations = self.validate_hard_constraints(site_data)
        technical_feasibility = len(critical_violations) == 0
        constraint_violations = len(critical_violations)

        feasibility_score = self.calculate_soft_constraint_score(site_data)
        overall_status = "Feasible" if technical_feasibility else "Unfeasible"

        return {
            "technical_feasibility": technical_feasibility,
            "technical_feasibility_score": int(feasibility_score),
            "constraint_violations": constraint_violations,
            "critical_violations": critical_violations,
            "overall_status": overall_status
        }
