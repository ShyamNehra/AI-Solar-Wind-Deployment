from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import requests
from app.db.postgres import get_db
from app.db.mongo import save_to_environmental_cache
from app.models.site import Site
from app.models.environmental import SiteEnvironmentalData
from app.models.user import User
from app.api.dependencies import get_current_user
from app.connectors.nasa_power import fetch_solar_data
from app.connectors.open_meteo_historical import fetch_historical_wind_data
from app.connectors.srtm import fetch_elevation
from app.connectors.osm import fetch_infrastructure_proximity
from app.connectors.copernicus import fetch_land_cover
from app.schemas.environmental import EnvironmentalDataOut
from geoalchemy2.shape import to_shape

router = APIRouter(prefix="/sites", tags=["Environmental Data"])

@router.post("/{site_id}/environmental/refresh", response_model=EnvironmentalDataOut)
def refresh_environmental_data(
    site_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Retrieve site
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")
        
    # Check permissions
    project = site.project
    user_roles = [role.name for role in current_user.roles]
    if "Administrator" not in user_roles and project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
    # 2. Extract lat/lon coordinates from geography POINT column
    point = to_shape(site.geom)
    longitude, latitude = point.x, point.y
    
    # 3. Fetch live data with 30s timeout handles
    # Solar Data (NASA POWER)
    try:
        solar_payload = fetch_solar_data(latitude, longitude)
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="NASA POWER API unreachable"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"NASA POWER API error: {str(e)}"
        )
        
    # Wind Data (Open-Meteo Historical)
    try:
        wind_payload = fetch_historical_wind_data(latitude, longitude)
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Open-Meteo Wind API unreachable"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Open-Meteo Wind API error: {str(e)}"
        )
        
    # Elevation Data (Open-Meteo Elevation)
    try:
        elevation_payload = fetch_elevation(latitude, longitude)
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Elevation API unreachable"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Elevation API error: {str(e)}"
        )
        
    # OSM Proximity Data
    try:
        osm_payload = fetch_infrastructure_proximity(latitude, longitude)
    except RuntimeError as e:
        if "504" in str(e) or "timeout" in str(e).lower() or "timed out" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail=f"Overpass API timeout: {str(e)}"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Overpass API error: {str(e)}"
            )

    # Copernicus Land Cover Data
    try:
        land_cover = fetch_land_cover(latitude, longitude)
    except ValueError as e:
        if "Copernicus credentials not configured" in str(e):
            land_cover = "PENDING_COPERNICUS_AUTH"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Copernicus config error: {str(e)}"
            )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Copernicus API error: {str(e)}"
        )
        
    # 4. Write payloads to MongoDB cache collection
    mongo_warnings = []
    
    ok1 = save_to_environmental_cache(latitude, longitude, "nasa_power", solar_payload)
    if not ok1:
        mongo_warnings.append("Failed to cache solar payload in MongoDB.")
        
    ok2 = save_to_environmental_cache(latitude, longitude, "open_meteo_wind", wind_payload)
    if not ok2:
        mongo_warnings.append("Failed to cache wind payload in MongoDB.")
        
    ok3 = save_to_environmental_cache(latitude, longitude, "open_meteo_elevation", elevation_payload)
    if not ok3:
        mongo_warnings.append("Failed to cache elevation payload in MongoDB.")
        
    ok4 = save_to_environmental_cache(latitude, longitude, "osm_proximity", osm_payload)
    if not ok4:
        mongo_warnings.append("Failed to cache OSM proximity in MongoDB.")
        
    ok5 = save_to_environmental_cache(latitude, longitude, "copernicus_land_cover", {"land_cover": land_cover})
    if not ok5:
        mongo_warnings.append("Failed to cache Copernicus land cover in MongoDB.")
        
    warnings_str = " ".join(mongo_warnings) if mongo_warnings else None
    
    # 5. Extract values
    avg_solar = solar_payload["properties"]["parameter"]["ALLSKY_SFC_SW_DWN"]["ANN"]
    avg_temp = solar_payload["properties"]["parameter"]["T2M"]["ANN"]
    
    # Recompute average_wind_speed as a time-averaged value from the 1-year hourly time-series
    speeds = [s for s in wind_payload["hourly"]["wind_speed_10m"] if s is not None]
    avg_wind_speed = round(sum(speeds) / len(speeds), 2) if speeds else 0.0
    
    dirs = [d for d in wind_payload["hourly"]["wind_direction_10m"] if d is not None]
    avg_wind_dir = round(sum(dirs) / len(dirs), 2) if dirs else 0.0
    
    avg_elevation = elevation_payload["elevation"][0]
    
    # 6. Update Postgres summary fields in site_environmental_data
    env_record = db.query(SiteEnvironmentalData).filter(SiteEnvironmentalData.site_id == site_id).first()
    if not env_record:
        env_record = SiteEnvironmentalData(
            site_id=site_id,
            average_solar_irradiance=avg_solar,
            average_wind_speed=avg_wind_speed,
            average_wind_direction=avg_wind_dir,
            average_temperature=avg_temp,
            average_elevation=avg_elevation,
            average_slope=0.0,
            land_cover_type=land_cover,
            nearest_road_km=osm_payload["nearest_road_km"],
            nearest_substation_km=osm_payload["nearest_substation_km"],
            nearest_urban_area_km=osm_payload["nearest_urban_area_km"],
            nearest_protected_zone_km=osm_payload["nearest_protected_zone_km"],
            nearest_water_body_km=osm_payload["nearest_water_body_km"]
        )
        db.add(env_record)
    else:
        env_record.average_solar_irradiance = avg_solar
        env_record.average_wind_speed = avg_wind_speed
        env_record.average_wind_direction = avg_wind_dir
        env_record.average_temperature = avg_temp
        env_record.average_elevation = avg_elevation
        env_record.land_cover_type = land_cover
        env_record.nearest_road_km = osm_payload["nearest_road_km"]
        env_record.nearest_substation_km = osm_payload["nearest_substation_km"]
        env_record.nearest_urban_area_km = osm_payload["nearest_urban_area_km"]
        env_record.nearest_protected_zone_km = osm_payload["nearest_protected_zone_km"]
        env_record.nearest_water_body_km = osm_payload["nearest_water_body_km"]
        
    # 7. Overwrite/Validate the site's elevation field using the live elevation data
    site.elevation = avg_elevation
    db.add(env_record)
    db.commit()
    db.refresh(env_record)
    
    # Create Copernicus blocker alert
    from app.models.notification import Notification
    if land_cover == "PENDING_COPERNICUS_AUTH":
        notif = Notification(
            user_id=current_user.id,
            title="Copernicus Credentials Pending",
            message="Copernicus Sentinel Hub credentials are not configured. Environmental analysis falls back to OSM features.",
            type="copernicus_blocker"
        )
        db.add(notif)
        db.commit()
    
    return EnvironmentalDataOut(
        id=env_record.id,
        site_id=env_record.site_id,
        average_solar_irradiance=env_record.average_solar_irradiance,
        average_wind_speed=env_record.average_wind_speed,
        average_wind_direction=env_record.average_wind_direction,
        average_temperature=env_record.average_temperature,
        average_elevation=env_record.average_elevation,
        average_slope=env_record.average_slope,
        land_cover_type=env_record.land_cover_type,
        nearest_road_km=env_record.nearest_road_km,
        nearest_substation_km=env_record.nearest_substation_km,
        nearest_urban_area_km=env_record.nearest_urban_area_km,
        nearest_protected_zone_km=env_record.nearest_protected_zone_km,
        nearest_water_body_km=env_record.nearest_water_body_km,
        last_fetched_at=env_record.last_fetched_at,
        data_sources={
            "solar": "NASA POWER Climatology",
            "wind": "Open-Meteo Historical Weather API",
            "elevation": "Open-Meteo Elevation API",
            "infrastructure": "OpenStreetMap Overpass API",
            "land_cover": "Copernicus Sentinel Hub"
        },
        warnings=warnings_str
    )
