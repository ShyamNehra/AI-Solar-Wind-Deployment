import uuid
from sqlalchemy import Column, String, Float, ForeignKey, DateTime, func
from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base


class Site(Base):
    __tablename__ = "sites"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    region = Column(String, nullable=True)
    land_area_sqkm = Column(Float, nullable=True)
    elevation_m = Column(Float, nullable=True)
    land_ownership = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="sites")
    environmental_data = relationship("EnvironmentalData", back_populates="site", uselist=False, cascade="all, delete-orphan")
    solar_prediction = relationship("SolarPrediction", back_populates="site", uselist=False, cascade="all, delete-orphan")
    wind_prediction = relationship("WindPrediction", back_populates="site", uselist=False, cascade="all, delete-orphan")
    suitability_score = relationship("SuitabilityScore", back_populates="site", uselist=False)
    id = Column(Integer, primary_key=True, index=True)
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

