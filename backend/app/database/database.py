from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Replace with your local pgAdmin/PostgreSQL credentials
DATABASE_URL = "postgresql://postgres:12345678@localhost:5432/solar_wind"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency to yield database sessions to your API routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()