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
    print("Seeding complete!")
except Exception as e:
    print(f"Error seeding database: {e}")
    db.rollback()
finally:
    db.close()
