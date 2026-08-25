from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from app.db.postgres import Base
from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base


class Site(Base):
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    # PostGIS geometry column using SRID 4326 (WGS84 lat/lon)
    geom = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    land_area = Column(Float, nullable=True)
    elevation = Column(Float, nullable=True)
    existing_infrastructure = Column(String(1000), nullable=True)
    land_ownership = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    project = relationship("Project", back_populates="sites")
    environmental_data = relationship("SiteEnvironmentalData", back_populates="site", cascade="all, delete-orphan", uselist=False)
    scores = relationship("SiteScore", back_populates="site", cascade="all, delete-orphan", uselist=False)
    forecast = relationship("EnergyForecast", back_populates="site", cascade="all, delete-orphan", uselist=False)

# Resolve relationship mappings
from app.models.environmental import SiteEnvironmentalData
from app.models.site_scores import SiteScore
from app.models.energy_forecast import EnergyForecast

    site_name = Column(String, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    elevation = Column(Float, nullable=True)
    land_area = Column(Float, nullable=True)
    region = Column(String, nullable=True)
    infrastructure = Column(String, nullable=True)
    ownership = Column(String, nullable=True)

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    project = relationship("Project", back_populates="sites")
    features = relationship("Feature", back_populates="site", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="site", cascade="all, delete-orphan")

