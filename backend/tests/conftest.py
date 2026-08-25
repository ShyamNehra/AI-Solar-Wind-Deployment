import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.postgres import Base
from app.models.user import User, Role

@pytest.fixture(scope="session")
def engine():
    return create_engine(settings.DATABASE_URL)

@pytest.fixture(scope="function")
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    
    # Create session
    Session = sessionmaker(bind=connection)
    session = Session()
    
    # Ensure roles are seeded (in case they are not in test environment)
    for role_name in ["Planner", "GIS Analyst", "Project Manager", "Administrator"]:
        if not session.query(Role).filter(Role.name == role_name).first():
            role = Role(name=role_name)
            session.add(role)
    session.commit()

    yield session
    
    session.close()
    transaction.rollback()
    connection.close()
