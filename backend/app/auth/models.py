import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text
from app.database.database import Base


class UserRole(str, enum.Enum):
    ENERGY_PLANNER = "renewable_energy_planner"
    GIS_ANALYST = "gis_analyst"
    PROJECT_MANAGER = "project_manager"
    ADMINISTRATOR = "administrator"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    organization = Column(String, nullable=True)
    organization_id = Column(String(50), default="ORG-INFOSYS-001", index=True, nullable=False)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.ENERGY_PLANNER, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)