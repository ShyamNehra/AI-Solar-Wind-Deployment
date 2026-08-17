import math
import requests
from typing import Dict, Any


NASA_POWER_URL = "https://power.larc.nasa.gov/api/temporal/climatology/point"
OPEN_METEO_ELEVATION_URL = "https://api.open-meteo.com/v1/elevation"


def _safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def get_nasa_power_data(latitude: float, longitude: float) -> Dict[str, float]:
    """
    Get location-dependent solar and wind resource data
    from NASA POWER climatology API.
    """

    params = {
        "parameters": "ALLSKY_SFC_SW_DWN,WS50M",
        "community": "RE",
        "longitude": longitude,
        "latitude": latitude,
        "format": "JSON",
    }

    response = requests.get(
        NASA_POWER_URL,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    properties = data.get("properties", {})
    parameter = properties.get("parameter", {})

    solar_values = parameter.get("ALLSKY_SFC_SW_DWN", {})
    wind_values = parameter.get("WS50M", {})

    solar = []
    wind = []

    for value in solar_values.values():
        value = _safe_float(value)
        if value > 0:
            solar.append(value)

    for value in wind_values.values():
        value = _safe_float(value)
        if value > 0:
            wind.append(value)

    solar_irradiance = (
        sum(solar) / len(solar)
        if solar
        else 0.0
    )

    wind_speed = (
        sum(wind) / len(wind)
        if wind
        else 0.0
    )

    return {
        "solar_irradiance": round(solar_irradiance, 3),
        "wind_speed": round(wind_speed, 3),
    }


def get_elevation(latitude: float, longitude: float) -> float:
    """
    Get elevation for the selected coordinate.
    """

    params = {
        "latitude": latitude,
        "longitude": longitude,
    }

    response = requests.get(
        OPEN_METEO_ELEVATION_URL,
        params=params,
        timeout=20,
    )

    response.raise_for_status()

    data = response.json()

    elevations = data.get("elevation", [])

    if not elevations:
        return 0.0

    return round(_safe_float(elevations[0]), 2)


def get_terrain_features(
    latitude: float,
    longitude: float,
) -> Dict[str, float]:
    """
    Estimate terrain slope from a small elevation neighbourhood.

    This is intentionally a lightweight terrain indicator for the
    current application. It is not a substitute for full-resolution
    DEM/GIS terrain processing.
    """

    center = get_elevation(latitude, longitude)

    delta = 0.01

    north = get_elevation(
        latitude + delta,
        longitude,
    )

    south = get_elevation(
        latitude - delta,
        longitude,
    )

    east = get_elevation(
        latitude,
        longitude + delta,
    )

    west = get_elevation(
        latitude,
        longitude - delta,
    )

    lat_distance_m = 111_320 * delta

    lon_distance_m = (
        111_320
        * math.cos(math.radians(latitude))
        * delta
    )

    if lat_distance_m <= 0:
        lat_distance_m = 1

    if lon_distance_m <= 0:
        lon_distance_m = 1

    north_south_gradient = (
        abs(north - south)
        / (2 * lat_distance_m)
    )

    east_west_gradient = (
        abs(east - west)
        / (2 * lon_distance_m)
    )

    gradient = math.sqrt(
        north_south_gradient ** 2
        + east_west_gradient ** 2
    )

    slope_degrees = math.degrees(
        math.atan(gradient)
    )

    return {
        "elevation": round(center, 2),
        "slope": round(slope_degrees, 2),
    }


def get_location_features(
    latitude: float,
    longitude: float,
) -> Dict[str, Any]:
    """
    Main location intelligence function.
    """

    resource = get_nasa_power_data(
        latitude,
        longitude,
    )

    terrain = get_terrain_features(
        latitude,
        longitude,
    )

    return {
        **resource,
        **terrain,
    }