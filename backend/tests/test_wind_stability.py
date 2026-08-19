import pytest
from sqlalchemy.orm import Session
from app.models.user import User, Role
from app.models.project import Project
from app.models.site import Site
from app.models.environmental import SiteEnvironmentalData
from app.services.suitability_engine import calculate_site_suitability
from app.services.scoring_engine import calculate_hybrid_score, map_score_to_category

def test_wind_score_stability_across_repeated_calls(db_session: Session):
    # 1. Setup mock User, Project, and Site
    planner_role = db_session.query(Role).filter(Role.name == "Planner").first()
    user = User(email="stability@example.com", hashed_password="hashed_password", is_active=True)
    user.roles.append(planner_role)
    db_session.add(user)
    db_session.commit()

    project = Project(name="Stability Project", owner_id=user.id)
    db_session.add(project)
    db_session.commit()

    site = Site(
        project_id=project.id,
        name="Stability Site",
        geom="SRID=4326;POINT(-115.5 34.5)"
    )
    db_session.add(site)
    db_session.commit()

    # 2. Setup SiteEnvironmentalData with stable average wind speed (time-averaged climatology)
    env_data = SiteEnvironmentalData(
        site_id=site.id,
        average_solar_irradiance=5.5,
        average_wind_speed=4.5,  # time-averaged climatology value
        average_wind_direction=180.0,
        average_temperature=20.0,
        average_elevation=200.0,
        average_slope=1.0,
        nearest_road_km=0.5,
        nearest_substation_km=1.0,
        nearest_protected_zone_km=10.0,
        nearest_water_body_km=10.0,
        land_cover_type="PENDING_COPERNICUS_AUTH"
    )
    db_session.add(env_data)
    db_session.commit()

    # 3. Call suitability calculation 3 times in immediate succession
    runs = []
    for _ in range(3):
        suit = calculate_site_suitability(site.id, db_session)
        solar_s = suit["solar"]["overall_deployment_score"]
        wind_s = suit["wind"]["overall_deployment_score"]
        hybrid = calculate_hybrid_score(solar_s, wind_s)
        runs.append((solar_s, wind_s, hybrid))

    # Assert that all runs returned identical results
    assert runs[0] == runs[1]
    assert runs[1] == runs[2]
    
    # Check that wind score is indeed computed
    assert runs[0][1] > 0.0
