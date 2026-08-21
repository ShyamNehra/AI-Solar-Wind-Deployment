"""Seed demo users for the Solar & Wind Deployment Intelligence Platform."""
import sys
sys.path.insert(0, '.')

from app.database.database import SessionLocal
from app.auth.models import User, UserRole
from app.auth.security import hash_password

db = SessionLocal()

demo_users = [
    {
        "email": "shyam@infosys.com",
        "username": "shyam_nehra",
        "password": "password123",
        "full_name": "Shyam Nehra",
        "organization": "Infosys Energy Division",
        "organization_id": "1001",
        "role": UserRole.ADMINISTRATOR
    },
    {
        "email": "aishwarya@infosys.com",
        "username": "aishwarya_r",
        "password": "password123",
        "full_name": "Aishwarya R.",
        "organization": "Infosys Energy Division",
        "organization_id": "1001",
        "role": UserRole.ENERGY_PLANNER
    },
    {
        "email": "rajesh@infosys.com",
        "username": "rajesh_kumar",
        "password": "password123",
        "full_name": "Rajesh Kumar",
        "organization": "Infosys Energy Division",
        "organization_id": "1001",
        "role": UserRole.PROJECT_MANAGER
    },
    {
        "email": "gis@infosys.com",
        "username": "gis_analyst",
        "password": "password123",
        "full_name": "GIS Analyst",
        "organization": "Infosys Energy Division",
        "organization_id": "1001",
        "role": UserRole.GIS_ANALYST
    },
    {
        "email": "lead@tatanewenergy.com",
        "username": "green_energy_lead",
        "password": "password123",
        "full_name": "Vikram Seth (Tata RE)",
        "organization": "Tata Renewable Energy",
        "organization_id": "2002",
        "role": UserRole.PROJECT_MANAGER
    }
]

try:
    print("=== SEEDING DEMO USERS ===")
    for u in demo_users:
        existing = db.query(User).filter((User.email == u["email"]) | (User.username == u["username"])).first()
        if not existing:
            new_user = User(
                email=u["email"],
                username=u["username"],
                hashed_password=hash_password(u["password"]),
                full_name=u["full_name"],
                organization=u["organization"],
                organization_id=u["organization_id"],
                role=u["role"]
            )
            db.add(new_user)
            print(f"Created demo user: {u['username']} ({u['role'].value}) -> {u['organization_id']}")
        else:
            existing.organization_id = u["organization_id"]
            existing.organization = u["organization"]
            print(f"Updated demo user workspace: {u['username']} -> {u['organization_id']}")
    db.commit()

    print("=== SEEDING DEFAULT SAVED SITES ===")
    from app.models.saved_site import SavedSite
    
    demo_sites = [
        {
            "org_ids": ["1001", "ORG-INFOSYS-001"],
            "name": "Bhadla Solar Park",
            "description": "High GHI Western Region location with adjacent substation.",
            "latitude": 27.5397,
            "longitude": 71.9152,
            "status": "APPROVED",
            "score": 94.8
        },
        {
            "org_ids": ["1001", "ORG-INFOSYS-001"],
            "name": "Khavda Renewable Energy Park",
            "description": "Hybrid wind-solar megawatt candidate site with clear road access.",
            "latitude": 23.8642,
            "longitude": 69.7339,
            "status": "UNDER_REVIEW",
            "score": 91.2
        },
        {
            "org_ids": ["1001", "ORG-INFOSYS-001", "2002"],
            "name": "Pavagada Solar Cluster",
            "description": "Southern Region high yield solar deployment zone.",
            "latitude": 14.1011,
            "longitude": 77.4363,
            "status": "FEASIBLE",
            "score": 88.5
        }
    ]

    for s in demo_sites:
        for org in s["org_ids"]:
            existing_site = db.query(SavedSite).filter(
                SavedSite.organization_id == org,
                SavedSite.name == s["name"]
            ).first()
            if not existing_site:
                new_site = SavedSite(
                    organization_id=org,
                    name=s["name"],
                    description=s["description"],
                    latitude=s["latitude"],
                    longitude=s["longitude"],
                    status=s["status"],
                    score=s["score"]
                )
                db.add(new_site)
                print(f"Created demo site '{s['name']}' for workspace '{org}'")

    db.commit()

    print("=== SEEDING DEFAULT RECENT SITES ===")
    from app.models.recent_site import RecentSite

    recent_demo_sites = [
        {
            "org_ids": ["1001", "ORG-INFOSYS-001"],
            "name": "Bhadla Solar Park",
            "latitude": 27.5397,
            "longitude": 71.9152,
            "status": "APPROVED",
            "region": "Western Region",
            "elevation": "220 Meters",
            "existing_infra": "Substation adjacent, Road access clear",
            "score": 94.8,
            "project_id": "PRJ-INFOSYS-01"
        },
        {
            "org_ids": ["1001", "ORG-INFOSYS-001"],
            "name": "Khavda Renewable Energy Park",
            "latitude": 23.8642,
            "longitude": 69.7339,
            "status": "APPROVED",
            "region": "Western Region",
            "elevation": "150 Meters",
            "existing_infra": "High voltage grid line nearby",
            "score": 91.2,
            "project_id": "PRJ-INFOSYS-02"
        }
    ]

    for rs in recent_demo_sites:
        for org in rs["org_ids"]:
            existing_rs = db.query(RecentSite).filter(
                RecentSite.organization_id == org,
                RecentSite.name == rs["name"]
            ).first()
            if not existing_rs:
                new_rs = RecentSite(
                    organization_id=org,
                    name=rs["name"],
                    latitude=rs["latitude"],
                    longitude=rs["longitude"],
                    status=rs["status"],
                    region=rs["region"],
                    elevation=rs["elevation"],
                    existing_infra=rs["existing_infra"],
                    score=rs["score"],
                    project_id=rs["project_id"],
                    evaluated_by="shyam_nehra"
                )
                db.add(new_rs)
                print(f"Created recent site '{rs['name']}' for workspace '{org}'")

    db.commit()
    print("Seeding complete!")
except Exception as e:
    print(f"Error seeding database: {e}")
    db.rollback()
finally:
    db.close()
