import pytest
from sqlalchemy.orm import Session
from geoalchemy2.shape import to_shape
from app.models.user import User, Role
from app.models.project import Project
from app.models.site import Site

def test_site_geometry_persistence_round_trip(db_session: Session):
    # 1. Create a dummy owner user
    planner_role = db_session.query(Role).filter(Role.name == "Planner").first()
    owner = User(email="testowner@example.com", hashed_password="hashed_password", is_active=True)
    owner.roles.append(planner_role)
    db_session.add(owner)
    db_session.commit()

    # 2. Create a project
    project = Project(name="Test Project", description="Test Desc", owner_id=owner.id)
    db_session.add(project)
    db_session.commit()

    # 3. Create a site with explicit PostGIS Point (SRID 4326)
    latitude, longitude = 37.7749, -122.4194
    wkt_geom = f"SRID=4326;POINT({longitude} {latitude})"
    
    site = Site(
        project_id=project.id,
        name="San Francisco Solar Site",
        geom=wkt_geom,
        land_area=15.5,
        elevation=16.0
    )
    db_session.add(site)
    db_session.commit()

    # 4. Fetch the site and test geometry round-trip
    fetched_site = db_session.query(Site).filter(Site.id == site.id).first()
    assert fetched_site is not None
    assert fetched_site.name == "San Francisco Solar Site"
    
    # Extract coordinates via shapely shape
    point = to_shape(fetched_site.geom)
    assert pytest.approx(point.x) == longitude
    assert pytest.approx(point.y) == latitude

def test_project_site_cascade_delete(db_session: Session):
    planner_role = db_session.query(Role).filter(Role.name == "Planner").first()
    owner = User(email="cascadeowner@example.com", hashed_password="hashed_password", is_active=True)
    owner.roles.append(planner_role)
    db_session.add(owner)
    db_session.commit()

    project = Project(name="Delete Me Project", owner_id=owner.id)
    db_session.add(project)
    db_session.commit()

    site = Site(
        project_id=project.id,
        name="Temp Site",
        geom="SRID=4326;POINT(0 0)"
    )
    db_session.add(site)
    db_session.commit()

    # Verify both exist
    assert db_session.query(Project).filter(Project.id == project.id).first() is not None
    assert db_session.query(Site).filter(Site.id == site.id).first() is not None

    # Delete the project
    db_session.delete(project)
    db_session.commit()

    # Verify project is deleted AND site is cascaded/deleted
    assert db_session.query(Project).filter(Project.id == project.id).first() is None
    assert db_session.query(Site).filter(Site.id == site.id).first() is None
