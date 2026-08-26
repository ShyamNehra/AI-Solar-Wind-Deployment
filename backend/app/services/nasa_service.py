import httpx
from fastapi import HTTPException, status

NASA_POWER_URL = "https://power.larc.nasa.gov/api/temporal/climatology/point"


async def fetch_nasa_environmental_data(latitude: float, longitude: float) -> dict:
    """Fetch climatology data from NASA POWER API for given coordinates."""
    params = {
        "parameters": "ALLSKY_SFC_SW_DWN,T2M,WS10M,PRECTOTCORR",
        "community": "RE",  # Renewable Energy community
        "longitude": longitude,
        "latitude": latitude,
        "format": "JSON"
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(NASA_POWER_URL, params=params)
            response.raise_for_status()
            data = response.json()

            # Extract annual parameter averages (keyed in uppercase 'ANN' by NASA API)
            parameter_dict = data.get("properties", {}).get("parameter", {})

            solar_irradiance = parameter_dict.get("ALLSKY_SFC_SW_DWN", {}).get("ANN", 4.5)
            temperature = parameter_dict.get("T2M", {}).get("ANN", 25.0)
            wind_speed = parameter_dict.get("WS10M", {}).get("ANN", 5.0)
            rainfall = parameter_dict.get("PRECTOTCORR", {}).get("ANN", 2.0)

            return {
                "solar_irradiance_kwh_m2": round(solar_irradiance, 2),
                "temperature_c": round(temperature, 2),
                "wind_speed_ms": round(wind_speed, 2),
                "rainfall_mm": round(rainfall * 365, 2)  # Convert daily average mm to annual total
            }

        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to communicate with NASA POWER API: {str(exc)}"
            )