import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.auth.security import create_access_token
from app.database.database import SessionLocal, Base, engine
from app.auth.models import User, UserRole

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    test_user = db.query(User).filter(User.username == "test_planner").first()
    if not test_user:
        test_user = User(
            email="test_planner@infosys.com",
            username="test_planner",
            hashed_password="hashed_test_pass",
            organization_id="1001",
            role=UserRole.ENERGY_PLANNER
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
    token = create_access_token({"sub": str(test_user.id)})
    yield {"user": test_user, "token": token}
    db.close()

def test_saved_sites_crud_pipeline(setup_test_db):
    headers = {"Authorization": f"Bearer {setup_test_db['token']}"}
    
    # 1. Fetch saved sites for organization_id=1001
    res = client.get("/sites/saved?organization_id=1001", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    
    # 2. Save a site
    payload = {
        "organization_id": "1001",
        "name": "Integration Test Favorite Site",
        "description": "Saved site for automated test validation",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "status": "APPROVED",
        "score": 95.0
    }
    save_res = client.post("/sites/saved", json=payload, headers=headers)
    assert save_res.status_code == 201
    saved_site = save_res.json()
    assert saved_site["name"] == "Integration Test Favorite Site"
    site_id = saved_site["id"]
    
    # 3. Delete saved site
    del_res = client.delete(f"/sites/saved/{site_id}?organization_id=1001", headers=headers)
    assert del_res.status_code == 200
    assert del_res.json()["id"] == site_id
