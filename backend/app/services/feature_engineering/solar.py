from app.data_sources.nasa_power import NASAPowerClient

class SolarService:
    """Orchestrates historical climate calculations using live satellite data entries."""
    
    def __init__(self, nasa_client: NASAPowerClient):
        self.nasa_client = nasa_client

    def calculate_solar_potential(self, latitude: float, longitude: float) -> dict:
        """Processes raw historical weather values into localized solar profiling metrics."""
        # Task 3: Call live data client cleanly instead of using static indicators
        live_metrics = self.nasa_client.get_solar_metrics(latitude, longitude)
        
        # Merge calculated variables alongside contextual engineering recommendations
        return {
            "solar_irradiance": live_metrics["solar_irradiance"],
            "temperature": live_metrics["temperature"],
            "humidity": live_metrics["humidity"],
            "optimal_panel_tilt_degrees": round(abs(latitude) * 0.87, 1)
        }