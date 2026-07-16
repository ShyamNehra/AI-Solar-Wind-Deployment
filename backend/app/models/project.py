from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from app.database.database import Base
from datetime import datetime, timezone # 1. Update this import line

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    state = Column(String(50), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # 2. Update 'default' here to use timezone-aware utcnow variant
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)