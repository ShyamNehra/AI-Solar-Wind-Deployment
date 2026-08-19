import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.postgres import get_db
from app.models.user import User, Role
from app.models.project import Project
from app.models.site import Site
from app.models.notification import Notification
from app.core.security import create_access_token

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

def test_notification_created_on_forecast_refresh(db_session: Session, client: TestClient):
    # 1. Setup user, project, site
    planner_role = db_session.query(Role).filter(Role.name == "Planner").first()
    owner = User(email="notif_owner@example.com", hashed_password="pw", is_active=True)
    owner.roles.append(planner_role)
    db_session.add(owner)
    db_session.commit()
    
    project = Project(name="Notif Project", owner_id=owner.id)
    db_session.add(project)
    db_session.commit()
    
    site = Site(project_id=project.id, name="Notif Site", geom="SRID=4326;POINT(-115 35)")
    db_session.add(site)
    db_session.commit()
    
    headers = get_auth_headers(owner.email)
    
    # 2. Mock forecast engine call and trigger seasonal forecast refresh route
    with patch("app.api.forecasting.generate_seasonal_forecast") as mock_gen:
        mock_gen.return_value = {
            "site_id": site.id,
            "solar_seasonal_kwh": {m: 100.0 for m in ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]},
            "wind_seasonal_kwh": {m: 100.0 for m in ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]},
            "formula_used": "mocked",
            "formula_source": "mocked"
        }
        
        response = client.post(f"/api/sites/{site.id}/forecast/seasonal", headers=headers)
        assert response.status_code == 200
        
    # 3. Verify notification record was created in the database
    notif = db_session.query(Notification).filter(Notification.user_id == owner.id).first()
    assert notif is not None
    assert notif.type == "forecast_refresh"
    assert "refreshed successfully" in notif.message
    
    # 4. Verify GET /api/notifications returns the notification list
    response = client.get("/api/notifications", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == notif.id
    assert data[0]["is_read"] is False
    
    # 5. Verify POST /api/notifications/{id}/read marks it as read
    response = client.post(f"/api/notifications/{notif.id}/read", headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Notification marked as read"
    
    db_session.refresh(notif)
    assert notif.is_read is True
