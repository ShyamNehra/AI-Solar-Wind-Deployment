from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, DateTime
from app.database.database import Base


class Feature(Base):
    """
    SQLAlchemy model representing the physical and meteorological features of a site.
    """
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
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
