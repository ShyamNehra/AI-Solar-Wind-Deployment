import pytest
from sqlalchemy.orm import Session
from app.db.mongo import raw_environmental_cache
from app.models.user import User, Role
from app.models.project import Project
from app.models.site import Site
from app.models.environmental import SiteEnvironmentalData
from app.services.forecasting_engine import (
    generate_seasonal_forecast,
    generate_longterm_projection,
    generate_revenue_forecast
)

def setup_test_forecast_site(db_session: Session) -> Site:
    # Seed user, project, site
    planner_role = db_session.query(Role).filter(Role.name == "Planner").first()
    user = User(email="forecast_test@example.com", hashed_password="password", is_active=True)
    user.roles.append(planner_role)
    db_session.add(user)
    db_session.commit()

    project = Project(name="Forecast Project", owner_id=user.id)
    db_session.add(project)
    db_session.commit()

    site = Site(
        project_id=project.id,
        name="Forecast Site",
        geom="SRID=4326;POINT(-115.5 34.5)",
        land_area=20000.0  # 20,000 sqm
    )
    db_session.add(site)
    db_session.commit()

    env_data = SiteEnvironmentalData(
        site_id=site.id,
        average_solar_irradiance=5.33,
        average_wind_speed=5.0,
        average_wind_direction=180.0,
        average_temperature=20.0,
        average_elevation=200.0,
        average_slope=0.0,
        nearest_road_km=0.5,
        nearest_substation_km=1.0,
        nearest_protected_zone_km=10.0,
        nearest_water_body_km=10.0,
        land_cover_type="PENDING_COPERNICUS_AUTH"
    )
    db_session.add(env_data)
    db_session.commit()
    return site

def test_seasonal_forecast_matches_nasa_power_monthly_data(db_session: Session):
    site = setup_test_forecast_site(db_session)
    lat, lon = 34.5, -115.5
    lat_key, lon_key = round(lat, 4), round(lon, 4)

    # 1. Seed mock NASA Power monthly data in Mongo
    solar_payload = {
        "properties": {
            "parameter": {
                "ALLSKY_SFC_SW_DWN": {
                    "JAN": 3.0, "FEB": 4.0, "MAR": 5.0, "APR": 6.0, "MAY": 7.0, "JUN": 8.0,
                    "JUL": 8.0, "AUG": 7.0, "SEP": 6.0, "OCT": 5.0, "NOV": 4.0, "DEC": 3.0, "ANN": 5.33
                },
                "T2M": {"ANN": 20.0}
            }
        }
    }
    raw_environmental_cache.update_one(
        {"lat": lat_key, "lon": lon_key, "source": "nasa_power"},
        {"$set": {"payload": solar_payload, "ingested_at": "2026-07-26"}},
        upsert=True
    )

    # 2. Seed mock Open-Meteo hourly wind data in Mongo
    wind_payload = {
        "hourly": {
            "time": [f"2025-{m:02d}-01T00:00" for m in range(1, 13)],
            "wind_speed_10m": [5.0] * 12,
            "wind_direction_10m": [180.0] * 12
        }
    }
    raw_environmental_cache.update_one(
        {"lat": lat_key, "lon": lon_key, "source": "open_meteo_wind"},
        {"$set": {"payload": wind_payload, "ingested_at": "2026-07-26"}},
        upsert=True
    )

    # 3. Call service
    res = generate_seasonal_forecast(site.id, db_session)
    
    # Verify Solar monthly value matching
    # JAN: 3.0 irradiance * 31 days * 0.20 eff * 0.75 pr * 5.0 area = 69.75 kWh
    assert res["solar_seasonal_kwh"]["JAN"] == 69.75
    # JUN: 8.0 irradiance * 30 days * 0.20 * 0.75 * 5.0 = 180.00 kWh
    assert res["solar_seasonal_kwh"]["JUN"] == 180.0

    # Clean cache
    raw_environmental_cache.delete_many({"lat": lat_key, "lon": lon_key})

def test_longterm_projection_degradation_applied_correctly(db_session: Session):
    site = setup_test_forecast_site(db_session)
    
    # 1. Call long-term projection service
    res = generate_longterm_projection(site.id, db_session)
    
    solar_projection = res["solar_longterm_kwh"]
    wind_projection = res["wind_longterm_kwh"]
    
    # Assert degradation rates are returned and valid
    assert res["degradation_rate_solar"] == 0.005
    assert res["degradation_rate_wind"] == 0.015
    
    # Verify Year 1 matches base prediction
    # Solar base expected_energy_output is (5.33 * 365.25) * 0.20 * 0.75 * 5.0 = 1460.09
    assert solar_projection[0] == 1460.09
    
    # Verify Year 20 matches degradation formula: base * (0.995^19)
    # 1460.09 * 0.909156... = 1327.45
    expected_y20 = round(1460.09 * ((1 - 0.005) ** 19), 2)
    assert solar_projection[19] == expected_y20
    assert solar_projection[19] == 1327.45  # Hand-verified calculation

def test_revenue_forecast_calculations(db_session: Session):
    site = setup_test_forecast_site(db_session)
    
    res = generate_revenue_forecast(site.id, db_session)
    
    # Expected rate = $0.125
    assert res["electricity_rate_usd_kwh"] == 0.125
    
    # Expected solar energy = 1460.09 kWh. Expected solar revenue = 1460.09 * 0.125 = 182.51
    assert res["solar_annual_revenue"] == 182.51
