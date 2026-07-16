from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from app.database.database import Base
from datetime import datetime, timezone

class Site(Base):
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True, index=True)
    # Links this land site to its parent project row
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    area_sq_meters = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)