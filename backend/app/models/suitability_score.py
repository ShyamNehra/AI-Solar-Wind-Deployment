import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base


class SuitabilityScore(Base):
    __tablename__ = "suitability_scores"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    site_id = Column(String, ForeignKey("sites.id", ondelete="CASCADE"), nullable=False, unique=True)

    overall_score = Column(Float, nullable=False)
    resource_score = Column(Float, nullable=True)  # <-- Added column here
    solar_score = Column(Float, nullable=True)
    wind_score = Column(Float, nullable=True)
    infrastructure_score = Column(Float, nullable=True)
    recommendation = Column(String, nullable=True)
    risks_json = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    site = relationship("Site", back_populates="suitability_score")