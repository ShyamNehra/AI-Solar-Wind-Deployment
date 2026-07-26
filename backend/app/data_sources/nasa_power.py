import requests
from fastapi import HTTPException

class NASAPowerClient:
    """Production client for extracting global historical solar radiation and climate vectors."""
    
    def __init__(self):
        # NASA POWER API regional point parameter resolution endpoint
        self.base_url = "https://power.larc.nasa.gov/api/temporal/climatology/point"

    def get_solar_metrics(self, latitude: float, longitude: float) -> dict:
        """
        Queries the NASA POWER API to fetch climatological data features.
        
        Target Parameter Keys:
            - ALLSKY_SFC_SW_DWN: Solar Irradiance (kW-hr/m^2/day)
            - T2M: Temperature at 2 Meters (°C)
            - RH2M: Relative Humidity at 2 Meters (%)
        """
        if not (-90.0 <= latitude <= 90.0) or not (-180.0 <= longitude <= 180.0):
            raise ValueError("Coordinates fall completely outside global spatial reference domains.")

        # Structure precise parameter matrix payload tokens
        params = {
            "parameters": "ALLSKY_SFC_SW_DWN,T2M,RH2M",
            "community": "RE",
            "longitude": longitude,
            "latitude": latitude,
            "format": "JSON"
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=502, 
                    detail=f"NASA POWER network backend failure. Status code: {response.status_code}"
                )
                
            raw_data = response.json()
            
            # Extract target parameter dictionaries safely from standard JSON trees
            parameter_root = raw_data.get("properties", {}).get("parameter", {})
            
            # The 'parameter' dictionary contains 'ALLSKY_SFC_SW_DWN', 'T2M', etc.
            # For climatology, it maps to a annual summary key 'PARAMETER_NAME': {'annual': value}
            solar_irradiance = parameter_root.get("ALLSKY_SFC_SW_DWN", {}).get("ANN", 0.0)
            temperature = parameter_root.get("T2M", {}).get("ANN", 0.0)
            humidity = parameter_root.get("RH2M", {}).get("ANN", 0.0)
            
            # Task 2 Requirement: Return only the clean structural parameter record
            return {
                "solar_irradiance": round(float(solar_irradiance), 2),
                "temperature": round(float(temperature), 2),
                "humidity": round(float(humidity), 2)
            }

        except requests.exceptions.Timeout:
            raise HTTPException(status_code=504, detail="NASA POWER connection gate timeout.")
        except requests.exceptions.RequestException as error:
            raise HTTPException(status_code=503, detail=f"External planetary API connection error: {str(error)}")