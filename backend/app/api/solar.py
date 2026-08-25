from fastapi import APIRouter, Query
from app.services.solar_service import SolarFeatureService

router = APIRouter()

solar_service = SolarFeatureService()


@router.get("/solar/features")
def get_solar_features(
    latitude: float = Query(..., description="Latitude"),
    longitude: float = Query(..., description="Longitude")
):
    return solar_service.get_solar_features(latitude, longitude)