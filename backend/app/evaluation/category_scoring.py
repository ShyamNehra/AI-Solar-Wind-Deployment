from app.evaluation.normalization import ScoreNormalization


class CategoryScoring:
    """
    Calculate category-wise suitability scores.
    """

    def __init__(self):
        self.normalizer = ScoreNormalization()

    def renewable_resource_score(self, solar_irradiance, wind_speed):
        """
        Renewable Resource Score
        """
        solar = self.normalizer.normalize_solar(solar_irradiance)
        wind = self.normalizer.normalize_wind(wind_speed)

        return (solar + wind) / 2

    def terrain_score(self, slope, elevation):
        """
        Terrain Score
        """
        slope_score = self.normalizer.normalize_slope(slope)

        # Lower elevation is assumed better
        elevation_score = max(100 - (elevation / 20), 0)

        return (slope_score + elevation_score) / 2

    def infrastructure_score(self, grid_distance, road_distance):
        """
        Infrastructure Score
        """
        grid = self.normalizer.normalize_grid_distance(grid_distance)
        road = self.normalizer.normalize_road_distance(road_distance)

        return (grid + road) / 2

    def environmental_score(self):
        """
        Placeholder environmental score.
        """
        return 80

    def economic_score(self):
        """
        Placeholder economic score.
        """
        return 75