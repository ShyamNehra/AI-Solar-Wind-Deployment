from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from app.database.database import Base
from datetime import datetime, timezone

class EnvironmentalData(Base):
    __tablename__ = "environmental_data"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id", ondelete="CASCADE"), nullable=False, index=True)
    
    data_source = Column(String(50), default="NASA_POWER", nullable=False)  # NASA_POWER, GWA, SRTM, Sentinel, OSM
    solar_irradiance = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    rainfall = Column(Float, nullable=True)
    cloud_cover = Column(Float, nullable=True)
    slope_percent = Column(Float, nullable=True)
    land_cover_type = Column(String(100), nullable=True)
    
    recorded_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
