from pydantic import BaseModel, Field

class Coordinate(BaseModel):
    """Reusable geographic coordinate representation."""
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)

def validate_coordinates(lat: float, lon: float) -> bool:
    """
    Checks if coordinates fall inside valid global limits.
    Returns True if valid, raises ValueError if out of bounds.
    """
    if not (-90.0 <= lat <= 90.0):
        raise ValueError(f"Latitude {lat} must be between -90 and 90 degrees.")
    if not (-180.0 <= lon <= 180.0):
        raise ValueError(f"Longitude {lon} must be between -180 and 180 degrees.")
    return True