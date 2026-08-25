from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.postgres import Base

class SiteScore(Base):
    __tablename__ = "site_scores"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    solar_score = Column(Float, nullable=True)
    wind_score = Column(Float, nullable=True)
    renewable_resource_score = Column(Float, nullable=True)
    geographic_score = Column(Float, nullable=True)
    infrastructure_score = Column(Float, nullable=True)
    environmental_score = Column(Float, nullable=True)
    economic_score = Column(Float, nullable=True)
    overall_deployment_score = Column(Float, nullable=True)
    suitability_category = Column(String(50), nullable=True)
    
    formula_used = Column(String(1000), nullable=True)
    formula_source = Column(String(1000), nullable=True)
    economic_score_note = Column(String(1000), nullable=True)
    environmental_score_note = Column(String(1000), nullable=True)
    infrastructure_score_note = Column(String(1000), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    site = relationship("Site", back_populates="scores")
