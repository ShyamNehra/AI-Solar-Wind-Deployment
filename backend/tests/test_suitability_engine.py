import pytest
from sqlalchemy.orm import Session
from app.models.user import User, Role
from app.models.project import Project
from app.models.site import Site
from app.models.environmental import SiteEnvironmentalData
from app.services.suitability_engine import calculate_site_suitability

def create_test_base(db_session: Session, email: str, project_name: str, site_name: str) -> Site:
    """Helper to set up basic DB entities for suitability testing."""
    planner_role = db_session.query(Role).filter(Role.name == "Planner").first()
    user = User(email=email, hashed_password="hashed_password", is_active=True)
    user.roles.append(planner_role)
    db_session.add(user)
    db_session.commit()

    project = Project(name=project_name, owner_id=user.id)
    db_session.add(project)
    db_session.commit()

    site = Site(
        project_id=project.id,
        name=site_name,
        geom="SRID=4326;POINT(-115.5 34.5)"
    )
    db_session.add(site)
    db_session.commit()
    return site

def test_protected_zone_exclusion_penalty(db_session: Session):
    # 1. Test Site A: Unconstrained (far from protected zones and water bodies)
    site_a = create_test_base(db_session, "usera@example.com", "Project A", "Site A")
    env_a = SiteEnvironmentalData(
        site_id=site_a.id,
        average_solar_irradiance=5.0,
        average_wind_speed=6.0,
        average_temperature=20.0,
        average_elevation=100.0,
        average_slope=0.0,
        nearest_road_km=0.5,
        nearest_substation_km=1.0,
        nearest_protected_zone_km=5.0,  # Far
        nearest_water_body_km=5.0,      # Far
        land_cover_type="Barren / Sparse Vegetation"
    )
    db_session.add(env_a)
    db_session.commit()
    
    suit_a = calculate_site_suitability(site_a.id, db_session)
    score_a = suit_a["solar"]["environmental_score"]
    
    # 2. Test Site B: Constrained (directly in protected zone)
    site_b = create_test_base(db_session, "userb@example.com", "Project B", "Site B")
    env_b = SiteEnvironmentalData(
        site_id=site_b.id,
        average_solar_irradiance=5.0,
        average_wind_speed=6.0,
        average_temperature=20.0,
        average_elevation=100.0,
        average_slope=0.0,
        nearest_road_km=0.5,
        nearest_substation_km=1.0,
        nearest_protected_zone_km=0.0,  # Directly in protected zone
        nearest_water_body_km=5.0,      # Far
        land_cover_type="Barren / Sparse Vegetation"
    )
    db_session.add(env_b)
    db_session.commit()
    
    suit_b = calculate_site_suitability(site_b.id, db_session)
    score_b = suit_b["solar"]["environmental_score"]
    
    # Verify environmental score is lower for Site B than Site A due to penalty
    assert score_b < score_a
    # Since pz_km is 0.0, protected_zone_score is 0.0. water_body_score is 100.0.
    # environmental_score = 0*0.5 + 100*0.5 = 50.0.
    assert score_b == 50.0
    
    # 3. Test Site C: Constrained (directly in water body)
    site_c = create_test_base(db_session, "userc@example.com", "Project C", "Site C")
    env_c = SiteEnvironmentalData(
        site_id=site_c.id,
        average_solar_irradiance=5.0,
        average_wind_speed=6.0,
        average_temperature=20.0,
        average_elevation=100.0,
        average_slope=0.0,
        nearest_road_km=0.5,
        nearest_substation_km=1.0,
        nearest_protected_zone_km=5.0,  # Far
        nearest_water_body_km=0.0,      # Directly in water
        land_cover_type="Barren / Sparse Vegetation"
    )
    db_session.add(env_c)
    db_session.commit()
    
    suit_c = calculate_site_suitability(site_c.id, db_session)
    score_c = suit_c["solar"]["environmental_score"]
    
    # Verify environmental score is lower for Site C than Site A due to penalty
    assert score_c < score_a
    # Since wb_km is 0.0, water_body_score is 0.0. protected_zone_score is 100.0.
    # environmental_score = 100*0.5 + 0*0.5 = 50.0.
    assert score_c == 50.0
