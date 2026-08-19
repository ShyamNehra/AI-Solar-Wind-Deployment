from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from app.database.database import Base
from datetime import datetime, timezone

class SuitabilityScore(Base):
    __tablename__ = "suitability_scores"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id", ondelete="CASCADE"), nullable=False, index=True)
    
    resource_score = Column(Float, nullable=False)
    geographic_score = Column(Float, nullable=False)
    infrastructure_score = Column(Float, nullable=False)
    environmental_score = Column(Float, nullable=False)
    economic_score = Column(Float, nullable=False)
    overall_score = Column(Float, nullable=False)
    
    suitability_category = Column(String(50), nullable=False)  # Excellent, Highly Suitable, Moderately Suitable, Low Suitability, Unsuitable
    calculated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
