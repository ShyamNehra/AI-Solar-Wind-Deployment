from fastapi import APIRouter, Depends, HTTPException, status
from app.data_sources.nasa_power import NASAPowerClient
from services.feature_engineering.solar import SolarFeatureEngineer

router = APIRouter(prefix="/solar", tags=["Solar"])


def get_nasa_client() -> NASAPowerClient:
    """
    FastAPI dependency that provides a NASAPowerClient instance.
    """
    return NASAPowerClient()


def get_solar_engineer(
    nasa_client: NASAPowerClient = Depends(get_nasa_client)
) -> SolarFeatureEngineer:
    """
    FastAPI dependency that provides a SolarFeatureEngineer instance.
    """
    return SolarFeatureEngineer(nasa_client=nasa_client)


@router.get("/features")
def get_solar_features(
    latitude: float,
    longitude: float,
    solar_engineer: SolarFeatureEngineer = Depends(get_solar_engineer)
):
    """
    Retrieve solar resource features (irradiance, temperature, and relative humidity)
    for the specified latitude and longitude from the NASA POWER API.
    """
    # Validation of coordinates
    if not (-90.0 <= latitude <= 90.0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Latitude must be between -90.0 and 90.0 degrees."
        )
    if not (-180.0 <= longitude <= 180.0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Longitude must be between -180.0 and 180.0 degrees."
        )

    try:
        features = solar_engineer.get_solar_features(latitude, longitude)
        return features
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except (ConnectionError, TimeoutError) as ce:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Network error connecting to NASA POWER API: {str(ce)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to fetch data from NASA POWER API: {str(e)}"
        )
