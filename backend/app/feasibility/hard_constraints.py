class HardConstraintValidator:
    """
    Validate mandatory technical constraints.
    """

    def validate(self, site):

        failed = []

        # -----------------------------
        # Solar Irradiance
        # -----------------------------

        if site.get("solar_irradiance", 0) < 5:
            failed.append("Low Solar Irradiance")

        # -----------------------------
        # Wind Speed
        # -----------------------------

        if site.get("wind_speed", 0) < 5:
            failed.append("Low Wind Speed")

        # -----------------------------
        # Terrain Slope
        # -----------------------------

        if site.get("slope", 0) > 15:
            failed.append("Steep Terrain")

        # -----------------------------
        # Distance to Grid
        # -----------------------------

        if site.get("distance_to_grid", 0) > 10:
            failed.append("Far From Grid")

        # -----------------------------
        # Final Decision
        # -----------------------------

        return {

            "passed": len(failed) == 0,

            "technical_feasibility": (
                "Technically Feasible"
                if len(failed) == 0
                else "Not Technically Feasible"
            ),

            "failed_constraints": failed

        }