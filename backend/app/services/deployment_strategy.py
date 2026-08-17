from app.services.hybrid_recommendation import HybridRecommendationService


class DeploymentStrategyService:
    """
    Service for recommending the best renewable energy
    deployment strategy.
    """

    def __init__(self):
        self.hybrid_service = HybridRecommendationService()

    def confidence_score(self, deployment: str):
        """
        Return confidence score based on deployment type.
        """

        scores = {
            "Solar": 88,
            "Wind": 87,
            "Hybrid": 91,
            "Further Analysis Required": 60
        }

        return scores.get(deployment, 50)

    def generate_reason(self, deployment: str):
        """
        Return explanation for the recommendation.
        """

        reasons = {
            "Solar":
                "High solar irradiance with limited wind resource.",

            "Wind":
                "Strong wind resource with relatively low solar potential.",

            "Hybrid":
                "High solar irradiance and consistently strong wind resource.",

            "Further Analysis Required":
                "Available data is insufficient for a clear recommendation."
        }

        return reasons.get(
            deployment,
            "No recommendation available."
        )

    def recommend_deployment(self, solar_irradiance: float, wind_speed: float):
        """
        Generate complete deployment recommendation.
        """

        deployment = self.hybrid_service.recommend(
            solar_irradiance,
            wind_speed
        )

        return {
            "deployment": deployment,
            "confidence": self.confidence_score(deployment),
            "reason": self.generate_reason(deployment)
        }