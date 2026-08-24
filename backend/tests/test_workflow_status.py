import json
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.auth.auth_handler import get_db, get_current_user
from app.database.database import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# In-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


def override_get_current_user():
    class MockUser:
        id = 1
        username = "testuser"
        email = "test@example.com"
        role = "Administrator"
    return MockUser()


client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def test_workflow_status_empty():
    res = client.get("/dashboard/workflow")
    assert res.status_code == 200
    data = res.json()
    assert data["project_created"] is False
    assert data["site_registered"] is False
    assert data["assessment_completed"] is False
    assert data["site_ranking_completed"] is False
    assert data["deployment_optimization_completed"] is False
    assert data["forecasting_completed"] is False
    assert data["investment_completed"] is False
    assert data["report_generated"] is False
    assert data["progress"] == 0


def test_workflow_status_project_and_site_created():
    # 1. Create Project
    client.post("/projects/", json={"project_name": "Test P1", "region": "North"})
    res = client.get("/dashboard/workflow")
    assert res.status_code == 200
    data = res.json()
    assert data["project_created"] is True
    assert data["progress"] == int(round((1 / 8.0) * 100))  # 13%

    # 2. Register Site (also extracts features)
    client.post("/sites/", json={"latitude": 12.34, "longitude": 56.78, "project_id": 1, "region": "North"})
    res2 = client.get("/dashboard/workflow")
    data2 = res2.json()
    assert data2["project_created"] is True
    assert data2["site_registered"] is True
    assert data2["assessment_completed"] is True
    assert data2["progress"] == int(round((3 / 8.0) * 100))  # 38%


def test_workflow_status_report_generated_triggers_completion():
    # Create project and site
    client.post("/projects/", json={"project_name": "Test P1", "region": "North"})
    client.post("/sites/", json={"latitude": 12.34, "longitude": 56.78, "project_id": 1, "region": "North"})
    
    # Perform assessment which generates ranking, optimization, forecasting, investment, assessment report
    client.get("/assessment?latitude=12.34&longitude=56.78")

    # Generate report
    client.post("/reports/", json={"title": "Test Report", "site_id": 1, "report_type": "Assessment"})

    res = client.get("/dashboard/workflow")
    assert res.status_code == 200
    data = res.json()
    assert data["project_created"] is True
    assert data["site_registered"] is True
    assert data["assessment_completed"] is True
    assert data["site_ranking_completed"] is True
    assert data["deployment_optimization_completed"] is True
    assert data["forecasting_completed"] is True
    assert data["investment_completed"] is True
    assert data["report_generated"] is True
    assert data["progress"] == 100


def test_workflow_status_reports_stat_greater_than_zero():
    # Create project, site, and run assessment (which generates an assessment record/report)
    client.post("/projects/", json={"project_name": "Test P1", "region": "North"})
    client.post("/sites/", json={"latitude": 12.34, "longitude": 56.78, "project_id": 1, "region": "North"})
    client.get("/assessment?latitude=12.34&longitude=56.78")

    stats_res = client.get("/dashboard/stats")
    assert stats_res.status_code == 200
    assert stats_res.json()["total_reports"] > 0

    workflow_res = client.get("/dashboard/workflow")
    assert workflow_res.status_code == 200
    data = workflow_res.json()
    assert data["report_generated"] is True
    assert data["progress"] == 100

