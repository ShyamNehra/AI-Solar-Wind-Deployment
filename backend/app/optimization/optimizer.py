class DeploymentOptimizer:
    """
    Determines the best deployment strategy,
    recommends installation capacity,
    analyzes future expansion feasibility,
    and generates a deployment plan.
    """

    def determine_deployment(
        self,
        solar_score,
        wind_score
    ):
        """
        Decide whether the site is best suited for
        Solar, Wind, or Hybrid deployment.
        """

        if solar_score >= 80 and wind_score >= 80:
            return "Hybrid"

        elif solar_score >= wind_score:
            return "Solar"

        else:
            return "Wind"

    def recommend_capacity(
        self,
        land_area,
        resource_score
    ):
        """
        Recommend installation capacity (MW)
        based on land area and resource score.
        """

        if land_area >= 100 and resource_score >= 80:
            return 100

        elif land_area >= 50 and resource_score >= 60:
            return 50

        elif land_area >= 20 and resource_score >= 40:
            return 20

        else:
            return 10

    def analyze_expansion(
        self,
        land_area,
        available_land_percent
    ):
        """
        Analyze future expansion feasibility.
        """

        if land_area >= 100 and available_land_percent >= 50:
            return "Expandable"

        elif land_area >= 50 and available_land_percent >= 25:
            return "Limited Expansion"

        else:
            return "Not Expandable"

    def generate_deployment_plan(
        self,
        solar_score,
        wind_score,
        land_area,
        resource_score,
        available_land_percent
    ):
        """
        Generate the final deployment plan.
        """

        technology = self.determine_deployment(
            solar_score,
            wind_score
        )

        capacity = self.recommend_capacity(
            land_area,
            resource_score
        )

        expansion = self.analyze_expansion(
            land_area,
            available_land_percent
        )

        remarks = []

        if technology == "Hybrid":
            remarks.append(
                "Site has strong solar and wind resources."
            )

        elif technology == "Solar":
            remarks.append(
                "Solar resource is stronger than wind."
            )

        else:
            remarks.append(
                "Wind resource is stronger than solar."
            )

        if expansion == "Expandable":
            remarks.append(
                "Future expansion is feasible."
            )

        elif expansion == "Limited Expansion":
            remarks.append(
                "Expansion is possible with some limitations."
            )

        else:
            remarks.append(
                "No significant future expansion possible."
            )

        return {
            "recommended_technology": technology,
            "recommended_capacity_mw": capacity,
            "expansion_status": expansion,
            "optimization_remarks": remarks
        }