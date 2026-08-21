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
    # Ensure test user exists
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

def test_recent_sites_crud_pipeline(setup_test_db):
    headers = {"Authorization": f"Bearer {setup_test_db['token']}"}
    
    # 1. Fetch recent sites for organization_id=1001
    res = client.get("/sites/recent?organization_id=1001", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    
    # 2. Post a new recent site evaluation for organization_id=1001
    payload = {
        "organization_id": "1001",
        "name": "Verify Site Test Park",
        "latitude": 26.9124,
        "longitude": 75.7873,
        "status": "APPROVED",
        "region": "Northern Region",
        "elevation": "430 Meters",
        "existing_infra": "Adjacent Substation",
        "score": 92.5,
        "project_id": "PRJ-TEST-99"
    }
    post_res = client.post("/sites/recent", json=payload, headers=headers)
    assert post_res.status_code == 201
    created = post_res.json()
    assert created["name"] == "Verify Site Test Park"
    assert created["organization_id"] == "1001"
    
    # 3. Fetch again and confirm newly added site appears at the top
    fetch_res = client.get("/sites/recent?organization_id=1001", headers=headers)
    assert fetch_res.status_code == 200
    recent_list = fetch_res.json()
    assert len(recent_list) > 0
    assert recent_list[0]["name"] == "Verify Site Test Park"
