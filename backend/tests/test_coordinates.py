import pytest

from app.utils.coordinates import (
    validate_latitude,
    validate_longitude,
    validate_coordinates,
    create_coordinate,
)


def test_valid_latitude():
    assert validate_latitude(20.2961)


def test_invalid_latitude():
    assert not validate_latitude(100)


def test_valid_longitude():
    assert validate_longitude(85.8245)


def test_invalid_longitude():
    assert not validate_longitude(200)


def test_valid_coordinates():
    assert validate_coordinates(20.2961, 85.8245)


def test_invalid_coordinates():
    assert not validate_coordinates(100, 250)


def test_create_coordinate():
    coord = create_coordinate(20.2961, 85.8245)

    assert coord.latitude == 20.2961
    assert coord.longitude == 85.8245


def test_create_invalid_coordinate():
    with pytest.raises(ValueError):
        create_coordinate(100, 250)
        