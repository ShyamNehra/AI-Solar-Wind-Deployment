from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.postgres import Base

class SiteEnvironmentalData(Base):
    __tablename__ = "site_environmental_data"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Metadata and summary environmental factors
    average_solar_irradiance = Column(Float, nullable=True)
    average_wind_speed = Column(Float, nullable=True)
    average_temperature = Column(Float, nullable=True)
    average_elevation = Column(Float, nullable=True)
    average_slope = Column(Float, nullable=True)
    average_wind_direction = Column(Float, nullable=True)
    land_cover_type = Column(String(255), nullable=True)
    
    # Proximity metrics (in kilometers)
    nearest_road_km = Column(Float, nullable=True)
    nearest_substation_km = Column(Float, nullable=True)
    nearest_urban_area_km = Column(Float, nullable=True)
    nearest_protected_zone_km = Column(Float, nullable=True)
    nearest_water_body_km = Column(Float, nullable=True)
    
    last_fetched_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    site = relationship("Site", back_populates="environmental_data")

# Resolve relationship mappings
from app.models.site import Site

