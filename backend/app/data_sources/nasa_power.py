class NASAPowerClient:
    """Client interface for interacting with historical solar radiation & climate data."""
    
    def __init__(self, dataset_path: str = "datasets/nasa_power/"):
        self.dataset_path = dataset_path

    def get_solar_metrics(self, latitude: float, longitude: float) -> dict:
        """
        Fetches historical solar radiation (kW-hr/m^2/day) and surface temperature.
        
        Inputs:
            latitude (float): Valid coordinate between -90.0 and 90.0
            longitude (float): Valid coordinate between -180.0 and 180.0
            
        Outputs:
            dict: Historical daily profiles mapping variables to values.
            
        Failures Raised:
            FileNotFoundError: If the source dataset directory path is invalid.
            ValueError: If coordinate arguments fall outside geographic boundaries.
        """
        # Placeholder signature for upcoming implementation layer
        pass