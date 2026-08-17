class TechnicalFeasibilityEngine:
    """
    Performs technical feasibility analysis.
    """

    def __init__(self):

        self.min_solar = 5.0
        self.min_wind = 5.0
        self.max_slope = 15
        self.max_grid_distance = 10

    def evaluate(self, site):

        # -----------------------------
        # Hard Constraints
        # -----------------------------

        failed_constraints = []

        if site.get("solar_irradiance", 0) < self.min_solar:
            failed_constraints.append("Low Solar Irradiance")

        if site.get("wind_speed", 0) < self.min_wind:
            failed_constraints.append("Low Wind Speed")

        if site.get("slope", 0) > self.max_slope:
            failed_constraints.append("Steep Terrain")

        if site.get("distance_to_grid", 0) > self.max_grid_distance:
            failed_constraints.append("Far From Grid")

        hard_pass = len(failed_constraints) == 0

        # -----------------------------
        # Soft Constraints
        # -----------------------------

        score = 100
        remarks = []

        # Distance to road
        if site.get("distance_to_road", 0) <= 1:
            remarks.append("Excellent road connectivity.")
        elif site.get("distance_to_road", 0) <= 3:
            score -= 10
            remarks.append("Moderate road connectivity.")
        else:
            score -= 25
            remarks.append("Poor road connectivity.")

        # Distance to grid
        if site.get("distance_to_grid", 0) <= 2:
            remarks.append("Grid is very close.")
        elif site.get("distance_to_grid", 0) <= 5:
            score -= 10
            remarks.append("Grid connection acceptable.")
        else:
            score -= 20
            remarks.append("Grid connection expensive.")

        # Land availability
        if site.get("available_land_percent", 100) < 50:
            score -= 15
            remarks.append("Limited usable land.")

        score = max(score, 0)

        return {

            "hard_constraints": {

                "passed": hard_pass,

                "technical_feasibility":
                    "Technically Feasible"
                    if hard_pass
                    else "Not Technically Feasible",

                "failed_constraints": failed_constraints

            },

            "soft_constraints": {

                "score": score,

                "remarks": remarks

            }

        }


if __name__ == "__main__":

    engine = TechnicalFeasibilityEngine()

    site = {

        "solar_irradiance": 5.8,
        "wind_speed": 6.5,
        "slope": 4,
        "distance_to_grid": 2,
        "distance_to_road": 1,
        "available_land_percent": 80

    }

    print(engine.evaluate(site))