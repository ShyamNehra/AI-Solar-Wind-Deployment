from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from app.database.database import Base
from datetime import datetime, timezone

class SolarPrediction(Base):
    __tablename__ = "solar_predictions"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id", ondelete="CASCADE"), nullable=False, index=True)
    
    annual_irradiance = Column(Float, nullable=True)
    peak_sun_hours = Column(Float, nullable=True)
    expected_energy_output_kwh = Column(Float, nullable=True)
    capacity_factor = Column(Float, nullable=True)
    performance_ratio = Column(Float, nullable=True)
    
    model_version = Column(String(50), default="XGBoost-RF-Ensemble-v1", nullable=False)
    predicted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
