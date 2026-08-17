from sqlalchemy.orm import Session

from app.models.feature import Feature
from app.schemas.feature import FeatureCreate


class FeatureStoreService:

    def save_feature(self, db: Session, feature: FeatureCreate):
        new_feature = Feature(
            latitude=feature.latitude,
            longitude=feature.longitude,
            solar_irradiance=feature.solar_irradiance,
            wind_speed=feature.wind_speed,
            temperature=feature.temperature,
            humidity=feature.humidity,
            elevation=feature.elevation,
            slope=feature.slope
        )

        db.add(new_feature)
        db.commit()
        db.refresh(new_feature)

        return new_feature

    def get_all_features(self, db: Session):
        return db.query(Feature).all()

    def get_feature_by_location(
        self,
        db: Session,
        latitude: float,
        longitude: float
    ):
        return (
            db.query(Feature)
            .filter(
                Feature.latitude == latitude,
                Feature.longitude == longitude
            )
            .first()
        )