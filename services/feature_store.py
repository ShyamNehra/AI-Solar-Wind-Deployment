from sqlalchemy.orm import Session
from app.models.feature import Feature
from schemas.feature import FeatureCreate


class FeatureStoreService:
    """
    Service responsible for database operations on Feature entities.
    """

    def save_feature(
        self,
        db: Session,
        feature_in: FeatureCreate
    ) -> Feature:
        """
        Store a new Feature record in the database.
        """
        db_feature = Feature(
            latitude=feature_in.latitude,
            longitude=feature_in.longitude,
            solar_irradiance=feature_in.solar_irradiance,
            wind_speed=feature_in.wind_speed,
            temperature=feature_in.temperature,
            humidity=feature_in.humidity,
            elevation=feature_in.elevation,
            slope=feature_in.slope
        )
        db.add(db_feature)
        db.commit()
        db.refresh(db_feature)
        return db_feature

    def get_all_features(self, db: Session) -> list[Feature]:
        """
        Retrieve all Feature records from the database.
        """
        return db.query(Feature).all()

    def get_feature_by_id(
        self,
        db: Session,
        feature_id: int
    ) -> Feature | None:
        """
        Retrieve a single Feature record by its ID.
        """
        return db.query(Feature).filter(Feature.id == feature_id).first()

    def get_feature_by_coordinates(
        self,
        db: Session,
        latitude: float,
        longitude: float
    ) -> Feature | None:
        """
        Retrieve a single Feature record by its coordinates.
        """
        return db.query(Feature).filter(
            Feature.latitude == latitude,
            Feature.longitude == longitude
        ).first()
