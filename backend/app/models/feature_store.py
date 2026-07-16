from sqlalchemy import Column, Integer, Float, DateTime
from app.database.database import Base
from datetime import datetime, timezone

class FeatureRecord(Base):
    __tablename__ = "feature_store"

    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    
    # Processed Machine Learning Features
    solar_irradiance = Column(Float, nullable=False)
    wind_speed = Column(Float, nullable=False)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    elevation = Column(Float, nullable=False)
    slope = Column(Float, nullable=False)
    
    # Metadata for debugging, tracking, and training pipelines
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))