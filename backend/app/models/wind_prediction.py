from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.postgres import Base

class WindPrediction(Base):
    __tablename__ = "wind_predictions"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id", ondelete="CASCADE"), nullable=False)
    
    average_wind_speed = Column(Float, nullable=False)
    wind_power_density = Column(Float, nullable=False)
    turbulence_intensity = Column(Float, nullable=False)
    capacity_factor = Column(Float, nullable=False)
    expected_annual_energy_production = Column(Float, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    site = relationship("Site")
