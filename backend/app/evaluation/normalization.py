class ScoreNormalization:
    """
    Normalize different environmental parameters
    to a common 0–100 scoring scale.
    """

    def normalize_solar(self, solar_irradiance: float):
        """
        Normalize solar irradiance (0–10 kWh/m²/day).
        """
        return min((solar_irradiance / 10) * 100, 100)

    def normalize_wind(self, wind_speed: float):
        """
        Normalize wind speed (0–10 m/s).
        """
        return min((wind_speed / 10) * 100, 100)

    def normalize_slope(self, slope: float):
        """
        Lower slope is better.
        """
        score = 100 - (slope * 5)
        return max(score, 0)

    def normalize_grid_distance(self, distance: float):
        """
        Smaller distance to grid is better.
        """
        score = 100 - (distance * 10)
        return max(score, 0)

    def normalize_road_distance(self, distance: float):
        """
        Smaller distance to road is better.
        """
        score = 100 - (distance * 10)
        return max(score, 0)