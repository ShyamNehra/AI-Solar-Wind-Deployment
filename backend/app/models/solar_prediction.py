import uuid
from sqlalchemy import Column, String, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database.database import Base


class SolarPrediction(Base):
    __tablename__ = "solar_predictions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    site_id = Column(String, ForeignKey("sites.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    annual_irradiance_kwh_m2 = Column(Float, nullable=False)
    peak_sun_hours = Column(Float, nullable=False)
    expected_energy_output_mwh = Column(Float, nullable=False)
    capacity_factor_pct = Column(Float, nullable=False)
    performance_ratio = Column(Float, nullable=False)
    panel_efficiency_pct = Column(Float, default=20.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    site = relationship("Site", back_populates="solar_prediction")
from sqlalchemy import Column, Integer, Float, DateTime
from sqlalchemy.sql import func
from app.database.database import Base

class SolarPrediction(Base):
    __tablename__ = "solar_predictions"

    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    predicted_irradiance = Column(Float, nullable=True)
    suitability_score = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
