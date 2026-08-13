import enum
import uuid
from sqlalchemy import Column, String, Boolean, Enum, DateTime, func
from sqlalchemy.orm import relationship
from app.database.database import Base


class UserRole(str, enum.Enum):
    PLANNER = "Renewable Energy Planner"
    GIS_ANALYST = "GIS Analyst"
    PROJECT_MANAGER = "Project Manager"
    ADMIN = "Administrator"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.PLANNER, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")