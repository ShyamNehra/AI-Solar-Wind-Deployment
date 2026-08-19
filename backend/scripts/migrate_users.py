"""Add missing columns to existing database tables dynamically."""
import sys
from pathlib import Path
from sqlalchemy import text, inspect

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.database.database import engine

def migrate_database():
    print("=== MIGRATING DATABASE COLUMNS ===")
    inspector = inspect(engine)
    
    with engine.connect() as conn:
        # 1. Users Table Migration
        if inspector.has_table("users"):
            user_cols = [c["name"] for c in inspector.get_columns("users")]
            print(f"Users columns: {user_cols}")
            if "bio" not in user_cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN bio TEXT"))
                print("Added: users.bio")
            if "avatar_url" not in user_cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN avatar_url VARCHAR"))
                print("Added: users.avatar_url")
            if "updated_at" not in user_cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN updated_at TIMESTAMP"))
                print("Added: users.updated_at")
            if "last_login" not in user_cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN last_login TIMESTAMP"))
                print("Added: users.last_login")
            if "organization_id" not in user_cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN organization_id VARCHAR(50) DEFAULT 'ORG-INFOSYS-001'"))
                print("Added: users.organization_id")

        # 2. Projects Table Migration
        if inspector.has_table("projects"):
            proj_cols = [c["name"] for c in inspector.get_columns("projects")]
            print(f"Projects columns: {proj_cols}")
            if "region" not in proj_cols:
                conn.execute(text("ALTER TABLE projects ADD COLUMN region VARCHAR(100)"))
                print("Added: projects.region")
            if "created_by" not in proj_cols:
                conn.execute(text("ALTER TABLE projects ADD COLUMN created_by INTEGER"))
                print("Added: projects.created_by")
            if "organization_id" not in proj_cols:
                conn.execute(text("ALTER TABLE projects ADD COLUMN organization_id VARCHAR(50) DEFAULT 'ORG-INFOSYS-001'"))
                print("Added: projects.organization_id")
            if "project_type" not in proj_cols:
                conn.execute(text("ALTER TABLE projects ADD COLUMN project_type VARCHAR(50) DEFAULT 'hybrid'"))
                print("Added: projects.project_type")
            if "status" not in proj_cols:
                conn.execute(text("ALTER TABLE projects ADD COLUMN status VARCHAR(50) DEFAULT 'active'"))
                print("Added: projects.status")

        # 3. Sites Table Migration
        if inspector.has_table("sites"):
            site_cols = [c["name"] for c in inspector.get_columns("sites")]
            print(f"Sites columns: {site_cols}")
            if "organization_id" not in site_cols:
                conn.execute(text("ALTER TABLE sites ADD COLUMN organization_id VARCHAR(50) DEFAULT 'ORG-INFOSYS-001'"))
                print("Added: sites.organization_id")
            if "region" not in site_cols:
                conn.execute(text("ALTER TABLE sites ADD COLUMN region VARCHAR(100)"))
                print("Added: sites.region")
            if "elevation_m" not in site_cols:
                conn.execute(text("ALTER TABLE sites ADD COLUMN elevation_m FLOAT"))
                print("Added: sites.elevation_m")
            if "land_ownership" not in site_cols:
                conn.execute(text("ALTER TABLE sites ADD COLUMN land_ownership VARCHAR(100)"))
                print("Added: sites.land_ownership")
            if "existing_infrastructure" not in site_cols:
                conn.execute(text("ALTER TABLE sites ADD COLUMN existing_infrastructure TEXT"))
                print("Added: sites.existing_infrastructure")

        conn.commit()
        print("Database migration complete!")

if __name__ == "__main__":
    migrate_database()
