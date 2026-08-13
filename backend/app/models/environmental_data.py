import uuid
from sqlalchemy import Column, String, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database.database import Base


class EnvironmentalData(Base):
    __tablename__ = "environmental_data"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    site_id = Column(String, ForeignKey("sites.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Solar & Weather factors
    solar_irradiance_kwh_m2 = Column(Float, nullable=True)
    temperature_c = Column(Float, nullable=True)
    cloud_cover_pct = Column(Float, nullable=True)
    rainfall_mm = Column(Float, nullable=True)
    
    # Wind factors
    wind_speed_ms = Column(Float, nullable=True)
    wind_direction_deg = Column(Float, nullable=True)
    
    # Geographic & Terrain factors
    elevation_m = Column(Float, nullable=True)
    land_slope_deg = Column(Float, nullable=True)
    vegetation_index_ndvi = Column(Float, nullable=True)
    
    # Infrastructure proximity (in km)
    distance_to_roads_km = Column(Float, nullable=True)
    distance_to_grid_km = Column(Float, nullable=True)
    distance_to_substation_km = Column(Float, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    site = relationship("Site", back_populates="environmental_data")