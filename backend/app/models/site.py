from sqlalchemy import Column, Integer, Float, String, Text, DateTime, ForeignKey
from app.database.database import Base
from datetime import datetime, timezone

class Site(Base):
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    organization_id = Column(String(50), default="ORG-INFOSYS-001", index=True, nullable=False)
    
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    region = Column(String(100), nullable=True)
    area_sq_meters = Column(Float, nullable=False)
    elevation_m = Column(Float, nullable=True)
    land_ownership = Column(String(100), nullable=True)
    existing_infrastructure = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)