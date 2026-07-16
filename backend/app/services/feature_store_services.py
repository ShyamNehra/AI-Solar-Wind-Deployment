from sqlalchemy.orm import Session
from app.models.feature_store import FeatureRecord
from app.schemas.feature_store import FeatureCreate

class FeatureStoreService:
    """Manages transactional caching, lookups, and archiving of engineered features."""

    @staticmethod
    def save_features(db: Session, feature_in: FeatureCreate) -> FeatureRecord:
        """Saves compiled machine learning parameters into the permanent data warehouse."""
        db_feature = FeatureRecord(**feature_in.model_dump())
        db.add(db_feature)
        db.commit()
        db.refresh(db_feature)
        return db_feature

    @staticmethod
    def get_all_features(db: Session) -> list[FeatureRecord]:
        """Retrieves every historic calculation pass captured inside the platform storage."""
        return db.query(FeatureRecord).all()

    @staticmethod
    def get_feature_by_id(db: Session, feature_id: int) -> FeatureRecord | None:
        """Locates an isolated calculation record using its absolute structural token."""
        return db.query(FeatureRecord).filter(FeatureRecord.id == feature_id).first()

    @staticmethod
    def lookup_cache(db: Session, lat: float, lon: float) -> FeatureRecord | None:
        """Looks up exact coordinate metrics to prevent running heavy spatial computations twice."""
        return db.query(FeatureRecord).filter(
            FeatureRecord.latitude == lat,
            FeatureRecord.longitude == lon
        ).first()