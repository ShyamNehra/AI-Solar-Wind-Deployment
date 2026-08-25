import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from app.connectors.nasa_power import fetch_solar_data
from app.db.mongo import raw_environmental_cache

def test_nasa_power_connector_parses_response():
    """
    Test that the NASA POWER connector makes the HTTP call and parses the JSON response correctly.
    This test uses mocks to prevent live API calls during unit testing.
    """
    mock_response_data = {
        "properties": {
            "parameter": {
                "ALLSKY_SFC_SW_DWN": {"ANN": 5.5},
                "T2M": {"ANN": 20.0}
            }
        }
    }
    
    with patch("requests.Session.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.json.return_value = mock_response_data
        mock_resp.status_code = 200
        mock_get.return_value = mock_resp
        
        data = fetch_solar_data(34.5, -115.5)
        
        # Verify the call details
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert "latitude=34.5" in args[0] or kwargs.get("params", {}).get("latitude") == 34.5
        assert "longitude=-115.5" in args[0] or kwargs.get("params", {}).get("longitude") == -115.5
        assert data["properties"]["parameter"]["ALLSKY_SFC_SW_DWN"]["ANN"] == 5.5
        assert data["properties"]["parameter"]["T2M"]["ANN"] == 20.0

def test_environmental_cache_ttl_index_active():
    """
    Test that the raw_environmental_cache collection has the TTL index on ingested_at active.
    """
    indexes = raw_environmental_cache.index_information()
    
    # Check that there is an index on 'ingested_at' and it has expireAfterSeconds set
    ttl_index_found = False
    for index_name, index_info in indexes.items():
        if index_info.get("key") == [("ingested_at", 1)]:
            assert index_info.get("expireAfterSeconds") == 2592000
            ttl_index_found = True
            break
            
    assert ttl_index_found, "TTL index on ingested_at not found"

from app.connectors.global_wind_atlas import fetch_wind_data
from app.connectors.srtm import fetch_elevation
from fastapi.testclient import TestClient
from app.main import app
import requests

def test_open_meteo_wind_connector_parses_response():
    mock_response_data = {
        "current": {
            "wind_speed_80m": 9.6,
            "wind_direction_80m": 257.0
        }
    }
    with patch("requests.Session.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.json.return_value = mock_response_data
        mock_resp.status_code = 200
        mock_get.return_value = mock_resp
        
        data = fetch_wind_data(34.5, -115.5)
        mock_get.assert_called_once()
        assert data["current"]["wind_speed_80m"] == 9.6
        assert data["current"]["wind_direction_80m"] == 257.0

def test_open_meteo_elevation_connector_parses_response():
    mock_response_data = {
        "elevation": [244.0]
    }
    with patch("requests.Session.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.json.return_value = mock_response_data
        mock_resp.status_code = 200
        mock_get.return_value = mock_resp
        
        data = fetch_elevation(34.5, -115.5)
        mock_get.assert_called_once()
        assert data["elevation"] == [244.0]

def test_nasa_power_timeout_fallback_simulation(db_session: Session):
    # Simulate a requests.exceptions.Timeout when refreshing site
    with patch("app.api.environmental.fetch_solar_data", side_effect=requests.exceptions.Timeout("Connection timed out")):
        from app.db.postgres import get_db
        def override_get_db():
            try:
                yield db_session
            finally:
                pass
        app.dependency_overrides[get_db] = override_get_db
        client = TestClient(app)
        from app.api.dependencies import get_current_user
        from app.models.user import User, Role
        from app.models.project import Project
        from app.models.site import Site
        
        planner_role = db_session.query(Role).filter(Role.name == "Planner").first()
        mock_user = User(email="planner_test_fallback@example.com", hashed_password="pw", is_active=True)
        mock_user.roles = [planner_role]
        db_session.add(mock_user)
        db_session.commit()

        project = Project(name="Test Project", owner_id=mock_user.id)
        db_session.add(project)
        db_session.commit()

        site = Site(project_id=project.id, name="Test Site", geom="SRID=4326;POINT(-115 35)")
        db_session.add(site)
        db_session.commit()
        
        app.dependency_overrides[get_current_user] = lambda: mock_user
        try:
            response = client.post(f"/api/sites/{site.id}/environmental/refresh")
            assert response.status_code == 504
            assert response.json()["detail"] == "NASA POWER API unreachable"
        finally:
            app.dependency_overrides.clear()


