from sqlalchemy import Column, Integer, Float, DateTime
from sqlalchemy.sql import func

from app.database.database import Base


class Feature(Base):
    __tablename__ = "features"

    id = Column(Integer, primary_key=True, index=True)

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    solar_irradiance = Column(Float, nullable=False)
    wind_speed = Column(Float, nullable=False)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)

    elevation = Column(Float, nullable=False)
    slope = Column(Float, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())