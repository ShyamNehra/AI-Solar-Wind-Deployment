from sqlalchemy import Column, Integer, Float, String, Text, DateTime
from app.database.database import Base
from datetime import datetime, timezone

class SavedSite(Base):
    __tablename__ = "saved_sites"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(String(50), index=True, nullable=False)
    name = Column(String(150), nullable=False)
    description = Column(String(100), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    status = Column(String(50), default="APPROVED", nullable=False)
    score = Column(Float, default=85.0, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
