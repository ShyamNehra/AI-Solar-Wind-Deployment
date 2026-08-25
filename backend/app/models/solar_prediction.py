from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.postgres import Base
from sqlalchemy import Column, Integer, Float, DateTime
from sqlalchemy.sql import func
from app.database.database import Base

class SolarPrediction(Base):
    __tablename__ = "solar_predictions"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id", ondelete="CASCADE"), nullable=False)
    
    annual_irradiance = Column(Float, nullable=False)
    peak_sun_hours = Column(Float, nullable=False)
    expected_energy_output = Column(Float, nullable=False)
    capacity_factor = Column(Float, nullable=False)
    performance_ratio = Column(Float, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    site = relationship("Site")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    predicted_irradiance = Column(Float, nullable=True)
    suitability_score = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
