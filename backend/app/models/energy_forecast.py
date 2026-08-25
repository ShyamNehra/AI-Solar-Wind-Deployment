from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.postgres import Base

class EnergyForecast(Base):
    __tablename__ = "energy_forecasts"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    solar_seasonal_kwh = Column(JSON, nullable=True)
    wind_seasonal_kwh = Column(JSON, nullable=True)
    solar_longterm_kwh = Column(JSON, nullable=True)
    wind_longterm_kwh = Column(JSON, nullable=True)
    
    solar_annual_revenue = Column(Float, nullable=True)
    wind_annual_revenue = Column(Float, nullable=True)
    combined_annual_revenue = Column(Float, nullable=True)
    
    electricity_rate_usd_kwh = Column(Float, nullable=True)
    grid_contribution_ratio = Column(Float, nullable=True)
    grid_contribution_note = Column(String(1000), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    site = relationship("Site", back_populates="forecast")
