from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from app.database.database import Base
from datetime import datetime, timezone

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    state = Column(String(50), nullable=True)
    region = Column(String(100), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    organization_id = Column(String(50), default="ORG-INFOSYS-001", index=True, nullable=False)
    project_type = Column(String(50), default="hybrid", nullable=False)  # solar, wind, hybrid
    status = Column(String(50), default="active", nullable=False)        # draft, active, completed
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)