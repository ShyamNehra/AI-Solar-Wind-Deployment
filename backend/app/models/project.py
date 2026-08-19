from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.postgres import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    owner = relationship("User")
    # Cascade delete sites if the project is deleted
    sites = relationship("Site", back_populates="project", cascade="all, delete-orphan")
    recommendation = relationship("DeploymentRecommendation", back_populates="project", cascade="all, delete-orphan", uselist=False)

from app.models.deployment_recommendation import DeploymentRecommendation
