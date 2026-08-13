import uuid
from sqlalchemy import Column, String, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database.database import Base


class WindPrediction(Base):
    __tablename__ = "wind_predictions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    site_id = Column(String, ForeignKey("sites.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    avg_wind_speed_ms = Column(Float, nullable=False)
    wind_power_density_w_m2 = Column(Float, nullable=False)
    turbulence_intensity = Column(Float, nullable=False)
    capacity_factor_pct = Column(Float, nullable=False)
    expected_annual_energy_mwh = Column(Float, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    site = relationship("Site", back_populates="wind_prediction")