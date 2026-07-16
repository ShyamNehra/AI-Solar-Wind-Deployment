from app.data_sources.nasa_power import NASAPowerClient

class SolarService:
    """Handles feature engineering and potential metrics for solar installations."""
    
    def __init__(self, nasa_client: NASAPowerClient):
        self.nasa_client = nasa_client

    def calculate_solar_potential(self, latitude: float, longitude: float) -> dict:
        """Processes raw climate data into actionable solar forecasting features."""
        raw_solar = self.nasa_client.get_solar_metrics(latitude, longitude)
        
        # Placeholders for upcoming Week 4 math modeling
        return {
            "estimated_annual_kwh_per_m2": 0.0,
            "peak_sun_hours_average": 0.0,
            "optimal_panel_tilt_degrees": latitude * 0.87,  # Rough geographic estimation rules
            "risk_factors": ["Cloud cover anomalies (Pending Data Extraction)"]
        }