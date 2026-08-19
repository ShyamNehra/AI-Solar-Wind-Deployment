from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from app.database.database import Base
from datetime import datetime, timezone

class WindPrediction(Base):
    __tablename__ = "wind_predictions"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id", ondelete="CASCADE"), nullable=False, index=True)
    
    average_wind_speed = Column(Float, nullable=True)
    wind_power_density = Column(Float, nullable=True)
    turbulence_intensity = Column(Float, nullable=True)
    capacity_factor = Column(Float, nullable=True)
    expected_annual_energy_kwh = Column(Float, nullable=True)
    
    model_version = Column(String(50), default="XGBoost-RF-Ensemble-v1", nullable=False)
    predicted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
