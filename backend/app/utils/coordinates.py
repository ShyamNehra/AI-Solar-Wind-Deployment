from dataclasses import dataclass


@dataclass
class Coordinate:
    latitude: float
    longitude: float


def validate_latitude(latitude: float) -> bool:
    """
    Validate latitude.
    Valid range: -90 to 90
    """
    return -90 <= latitude <= 90


def validate_longitude(longitude: float) -> bool:
    """
    Validate longitude.
    Valid range: -180 to 180
    """
    return -180 <= longitude <= 180


def validate_coordinates(latitude: float, longitude: float) -> bool:
    """
    Validate both latitude and longitude.
    """
    return (
        validate_latitude(latitude)
        and validate_longitude(longitude)
    )


def create_coordinate(latitude: float, longitude: float) -> Coordinate:
    """
    Create a Coordinate object after validation.
    """

    if not validate_coordinates(latitude, longitude):
        raise ValueError("Invalid latitude or longitude")

    return Coordinate(
        latitude=latitude,
        longitude=longitude
    )