import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.postgres import get_db
from app.models.user import User, Role
from app.models.project import Project
from app.models.site import Site
from app.models.site_scores import SiteScore
from app.core.security import create_access_token

# Disclosures
from app.services.suitability_engine import (
    ENVIRONMENTAL_SCORE_NOTE,
    INFRASTRUCTURE_SCORE_NOTE,
    ECONOMIC_SCORE_NOTE
)
from app.api.predictions import (
    WIND_CAP_FACTOR_NOTE
)
from app.services.forecasting_engine import (
    GRID_CONTRIBUTION_NOTE,
    ELECTRICITY_RATE_SOURCE
)

@pytest.fixture
def client(db_session: Session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

def get_auth_headers(email: str) -> dict:
    token = create_access_token(subject=email)
    return {"Authorization": f"Bearer {token}"}

def test_admin_data_sources_reflects_live_disclosures(db_session: Session, client: TestClient):
    # 1. Create admin user
    admin_role = db_session.query(Role).filter(Role.name == "Administrator").first()
    admin = User(email="admin_disclosure@example.com", hashed_password="pw", is_active=True)
    admin.roles.append(admin_role)
    db_session.add(admin)
    db_session.commit()
    
    headers = get_auth_headers(admin.email)
    
    # 2. Call GET /api/admin/data-sources
    response = client.get("/api/admin/data-sources", headers=headers)
    assert response.status_code == 200
    data = response.json()
    
    # 3. Assert live imported constants are returned
    keys_map = {item["key"]: item["disclosure"] for item in data}
    assert keys_map["wind_capacity_factor"] == WIND_CAP_FACTOR_NOTE
    assert keys_map["economic_feasibility"] == ECONOMIC_SCORE_NOTE
    assert keys_map["environmental_impact"] == ENVIRONMENTAL_SCORE_NOTE
    assert keys_map["grid_contribution"] == GRID_CONTRIBUTION_NOTE
    assert keys_map["electricity_price"] == ELECTRICITY_RATE_SOURCE
    assert keys_map["infrastructure_proximity"] == INFRASTRUCTURE_SCORE_NOTE

def test_role_specific_dashboards_rbac_and_data(db_session: Session, client: TestClient):
    # Setup test users
    planner_role = db_session.query(Role).filter(Role.name == "Planner").first()
    gis_role = db_session.query(Role).filter(Role.name == "GIS Analyst").first()
    pm_role = db_session.query(Role).filter(Role.name == "Project Manager").first()
    
    planner = User(email="p_dash@example.com", hashed_password="pw", is_active=True)
    planner.roles.append(planner_role)
    
    gis = User(email="g_dash@example.com", hashed_password="pw", is_active=True)
    gis.roles.append(gis_role)
    
    pm = User(email="pm_dash@example.com", hashed_password="pw", is_active=True)
    pm.roles.append(pm_role)
    
    db_session.add_all([planner, gis, pm])
    db_session.commit()
    
    # Create project and site owned by PM
    proj = Project(name="PM Project", owner_id=pm.id)
    db_session.add(proj)
    db_session.commit()
    
    site = Site(project_id=proj.id, name="Dash Site", geom="SRID=4326;POINT(-115 35)")
    db_session.add(site)
    db_session.commit()
    
    score = SiteScore(
        site_id=site.id,
        overall_deployment_score=80.0,
        suitability_category="High Suitability",
        solar_score=85.0,
        wind_score=75.0,
        geographic_score=80.0,
        infrastructure_score=80.0,
        environmental_score=80.0,
        economic_score=80.0
    )
    db_session.add(score)
    db_session.commit()
    
    # Test Planner Dashboard Access
    planner_headers = get_auth_headers(planner.email)
    # Planner doesn't own project, so forbidden
    res = client.get(f"/api/dashboards/planner/{proj.id}", headers=planner_headers)
    assert res.status_code == 403
    
    # Make planner owner or PM access
    pm_headers = get_auth_headers(pm.email)
    res = client.get(f"/api/dashboards/planner/{proj.id}", headers=pm_headers)
    assert res.status_code == 200
    assert "recommended_sites" in res.json()
    
    # Test GIS Analyst Dashboard Access
    res = client.get(f"/api/dashboards/gis-analyst/{proj.id}", headers=pm_headers)
    assert res.status_code == 200
    assert "gis_analyst_data" in res.json()
    
    # Test PM Dashboard Access
    res = client.get(f"/api/dashboards/project-manager/{proj.id}", headers=pm_headers)
    assert res.status_code == 200
    assert "overall_project_readiness" in res.json()
    assert "expansion_risk_flags" in res.json()
