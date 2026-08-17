from functools import lru_cache

import geopandas as gpd
import geodatasets
from shapely.geometry import Point


# ============================================================
# SETTINGS
# ============================================================

# Coastal warning distance
COASTAL_BUFFER_KM = 2.0


# ============================================================
# LOAD LAND DATA
# ============================================================

@lru_cache(maxsize=1)
def load_land_polygons():

    land_path = geodatasets.get_path(
        "naturalearth.land"
    )

    land = gpd.read_file(land_path)

    # Original geographic coordinates
    land = land.to_crs("EPSG:4326")

    return land


# ============================================================
# VALIDATE LOCATION
# ============================================================

def validate_location(
    latitude: float,
    longitude: float
):

    # --------------------------------------------------------
    # Coordinate validation
    # --------------------------------------------------------

    if not -90 <= latitude <= 90:

        return {
            "valid": False,
            "location_type": "Invalid Latitude",
            "reason": "Latitude must be between -90 and 90.",
            "is_land": False,
            "is_coastal": False
        }

    if not -180 <= longitude <= 180:

        return {
            "valid": False,
            "location_type": "Invalid Longitude",
            "reason": "Longitude must be between -180 and 180.",
            "is_land": False,
            "is_coastal": False
        }

    # --------------------------------------------------------
    # India analysis region
    # --------------------------------------------------------

    if not (
        6.0 <= latitude <= 37.5
        and 68.0 <= longitude <= 98.0
    ):

        return {
            "valid": False,
            "location_type": "Outside Analysis Region",
            "reason": (
                "Location is outside the supported "
                "India analysis region."
            ),
            "is_land": False,
            "is_coastal": False
        }

    # --------------------------------------------------------
    # Load land
    # --------------------------------------------------------

    try:

        land = load_land_polygons()

        point = Point(
            longitude,
            latitude
        )

        # ----------------------------------------------------
        # Exact land test
        # ----------------------------------------------------

        is_land = land.geometry.contains(point).any()

        # ----------------------------------------------------
        # Convert to metric CRS
        # ----------------------------------------------------
        #
        # EPSG:3857 gives distances in metres.
        #
        # This is much better than measuring raw latitude/
        # longitude degrees.
        # ----------------------------------------------------

        land_metric = land.to_crs("EPSG:3857")

        point_metric = gpd.GeoSeries(
            [point],
            crs="EPSG:4326"
        ).to_crs("EPSG:3857").iloc[0]

        # ----------------------------------------------------
        # Distance to nearest coastline
        # ----------------------------------------------------

        coastline = land_metric.geometry.boundary

        nearest_distance_m = coastline.distance(
            point_metric
        ).min()

        nearest_distance_km = (
            nearest_distance_m / 1000.0
        )

        # ----------------------------------------------------
        # COASTAL BOUNDARY
        # ----------------------------------------------------
        #
        # Check this BEFORE land/water classification.
        #
        # This means a point very close to the coastline
        # gets the safer "Coastal Boundary" response.
        # ----------------------------------------------------

        if nearest_distance_km <= COASTAL_BUFFER_KM:

            return {
                "valid": False,
                "location_type": "Coastal Boundary",
                "reason": (
                    f"Selected location is approximately "
                    f"{nearest_distance_km:.2f} km from the "
                    "coastline. Please select a point "
                    "slightly inland for reliable analysis."
                ),
                "is_land": bool(is_land),
                "is_coastal": True,
                "distance_to_coast_km": round(
                    nearest_distance_km,
                    3
                )
            }

        # ----------------------------------------------------
        # LAND
        # ----------------------------------------------------

        if is_land:

            return {
                "valid": True,
                "location_type": "Land",
                "reason": (
                    "Selected coordinate is sufficiently "
                    "inland and suitable for site analysis."
                ),
                "is_land": True,
                "is_coastal": False,
                "distance_to_coast_km": round(
                    nearest_distance_km,
                    3
                )
            }

        # ----------------------------------------------------
        # WATER
        # ----------------------------------------------------

        return {
            "valid": False,
            "location_type": "Water",
            "reason": (
                "Selected coordinate is in a water region. "
                "Land-based renewable deployment analysis "
                "cannot be performed here."
            ),
            "is_land": False,
            "is_coastal": False,
            "distance_to_coast_km": round(
                nearest_distance_km,
                3
            )
        }

    except Exception as e:

        return {
            "valid": False,
            "location_type": "Validation Error",
            "reason": (
                "Unable to determine land/water status: "
                f"{str(e)}"
            ),
            "is_land": False,
            "is_coastal": False
        }