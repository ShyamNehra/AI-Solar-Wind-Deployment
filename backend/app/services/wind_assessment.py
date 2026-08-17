class WindAssessmentService:
    """
    Service for assessing wind energy potential.
    """

    def calculate_wind_class(self, wind_speed: float):
        """
        Classify the wind resource based on wind speed.
        """

        if wind_speed < 3:
            return "Poor"

        elif wind_speed < 5:
            return "Moderate"

        elif wind_speed < 7:
            return "Good"

        else:
            return "Excellent"

    def calculate_capacity_factor(self, wind_speed: float):
        """
        Estimate wind turbine capacity factor.
        """

        if wind_speed < 3:
            return 0.10

        elif wind_speed < 5:
            return 0.25

        elif wind_speed < 7:
            return 0.40

        else:
            return 0.55

    def classify_wind_site(self, wind_speed: float):
        """
        Return both wind class and capacity factor.
        """

        return {
            "wind_class": self.calculate_wind_class(wind_speed),
            "capacity_factor": self.calculate_capacity_factor(wind_speed)
        }