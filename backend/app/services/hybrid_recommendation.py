class HybridRecommendationService:
    """
    Service to recommend the best renewable energy deployment.
    """

    def recommend(self, solar_irradiance: float, wind_speed: float):
        """
        Recommend Solar, Wind, or Hybrid based on
        solar irradiance and wind speed.
        """

        # Excellent Solar + Poor Wind
        if solar_irradiance >= 5 and wind_speed < 3:
            return "Solar"

        # Poor Solar + Excellent Wind
        elif solar_irradiance < 5 and wind_speed >= 7:
            return "Wind"

        # Excellent Solar + Excellent Wind
        elif solar_irradiance >= 5 and wind_speed >= 7:
            return "Hybrid"

        # Good Solar + Good Wind
        elif solar_irradiance >= 4 and wind_speed >= 5:
            return "Hybrid"

        # Default
        else:
            return "Further Analysis Required"