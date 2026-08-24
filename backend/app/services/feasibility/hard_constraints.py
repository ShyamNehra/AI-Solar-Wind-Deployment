"""
Hard Constraint Validation Module.
Evaluates mandatory engineering constraints for renewable site deployment.
If any hard constraint is violated, the site is immediately marked as NOT FEASIBLE.
"""

from typing import Dict, Any, List, Tuple
from app.services.feasibility.models import HardConstraintResult

DEFAULT_SLOPE_THRESHOLD_DEGREES = 35.0


class HardConstraintValidator:
    """
    Validates mandatory engineering constraints:
    - Restricted Land Use
    - Protected Forest Area
    - Water Bodies
    - National Parks
    - Military Zones
    - Airport Restricted Area
    - Slope > acceptable threshold (default 35.0°)
    - Unsafe Terrain
    - Flood Zone
    - Severe Environmental Restrictions
    """

    def validate(
        self,
        features: Dict[str, Any],
        max_slope_degrees: float = DEFAULT_SLOPE_THRESHOLD_DEGREES
    ) -> HardConstraintResult:
        """
        Evaluates input feature dictionary against mandatory hard engineering constraints.
        Returns HardConstraintResult with passed boolean and list of violations.
        """
        violations: List[str] = []

        # 1. Protected Forest Area
        if features.get("protected_forest") or features.get("protected_forest_area") or features.get("is_protected_forest"):
            violations.append("Protected Forest Area")

        # 2. Restricted Land Use
        if features.get("restricted_land_use") or features.get("land_use_restricted"):
            violations.append("Restricted Land Use")

        # 3. Water Bodies
        if features.get("water_body") or features.get("is_water_body") or features.get("water_body_area"):
            violations.append("Water Body Zone")

        # 4. National Parks
        if features.get("national_park") or features.get("is_national_park"):
            violations.append("National Park Area")

        # 5. Military Zones
        if features.get("military_zone") or features.get("is_military_zone"):
            violations.append("Military Restricted Zone")

        # 6. Airport Restricted Area
        if features.get("airport_restricted_area") or features.get("is_airport_zone"):
            violations.append("Airport Restricted Area")

        # 7. Flood Zone
        if features.get("flood_zone") or features.get("is_flood_zone"):
            violations.append("Flood Zone Hazard")

        # 8. Unsafe Terrain
        if features.get("unsafe_terrain") or features.get("is_unsafe_terrain"):
            violations.append("Unsafe Geological Terrain")

        # 9. Severe Environmental Restrictions
        if features.get("severe_environmental_restrictions") or features.get("environmental_restriction"):
            violations.append("Severe Environmental Restrictions")

        # 10. Slope Threshold (> 35° or passed max_slope_degrees)
        slope = float(features.get("slope", 0.0) or 0.0)
        if slope > max_slope_degrees:
            violations.append(f"Slope > {max_slope_degrees:g}° ({slope:.1f}°)")

        passed = len(violations) == 0

        return HardConstraintResult(
            passed=passed,
            violations=violations
        )
