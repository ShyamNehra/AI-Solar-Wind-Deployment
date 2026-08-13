from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.database import get_db
from app.models.environmental_data import EnvironmentalData
from app.models.site import Site
from app.models.user import User
from app.schemas.environmental_data import EnvironmentalDataResponse
from app.services.nasa_service import fetch_nasa_environmental_data
from app.services.osm_service import fetch_osm_infrastructure_distances

router = APIRouter(prefix="/environmental", tags=["Environmental Data"])


@router.post("/fetch/{site_id}", response_model=EnvironmentalDataResponse, status_code=status.HTTP_200_OK)
async def fetch_and_store_site_data(
    site_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetch environmental (NASA) and proximity (OSM) data and store in PostgreSQL."""
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    # Fetch NASA climate metrics & OSM infrastructure metrics
    nasa_data = await fetch_nasa_environmental_data(site.latitude, site.longitude)
    osm_data = await fetch_osm_infrastructure_distances(site.latitude, site.longitude)

    env_record = db.query(EnvironmentalData).filter(EnvironmentalData.site_id == site_id).first()

    if env_record:
        env_record.solar_irradiance_kwh_m2 = nasa_data["solar_irradiance_kwh_m2"]
        env_record.temperature_c = nasa_data["temperature_c"]
        env_record.wind_speed_ms = nasa_data["wind_speed_ms"]
        env_record.rainfall_mm = nasa_data["rainfall_mm"]
        env_record.distance_to_roads_km = osm_data["distance_to_roads_km"]
        env_record.distance_to_grid_km = osm_data["distance_to_grid_km"]
        env_record.distance_to_substation_km = osm_data["distance_to_substation_km"]
    else:
        env_record = EnvironmentalData(
            site_id=site_id,
            solar_irradiance_kwh_m2=nasa_data["solar_irradiance_kwh_m2"],
            temperature_c=nasa_data["temperature_c"],
            wind_speed_ms=nasa_data["wind_speed_ms"],
            rainfall_mm=nasa_data["rainfall_mm"],
            elevation_m=site.elevation_m or 100.0,
            distance_to_roads_km=osm_data["distance_to_roads_km"],
            distance_to_grid_km=osm_data["distance_to_grid_km"],
            distance_to_substation_km=osm_data["distance_to_substation_km"]
        )
        db.add(env_record)

    db.commit()
    db.refresh(env_record)
    return env_record


@router.get("/{site_id}", response_model=EnvironmentalDataResponse)
def get_site_environmental_data(
    site_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve existing environmental data for a given site."""
    env_record = db.query(EnvironmentalData).filter(EnvironmentalData.site_id == site_id).first()
    if not env_record:
        raise HTTPException(status_code=404, detail="Environmental data not found for this site")
    return env_record