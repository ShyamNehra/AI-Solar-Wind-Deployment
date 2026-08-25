from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas.feature import FeatureResponse, FeatureCreate
from services.feature_store import FeatureStoreService
from app.database.database import SessionLocal

router = APIRouter(prefix="/features", tags=["Features"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


feature_service = FeatureStoreService()


@router.get("", response_model=list[FeatureResponse])
def get_features(db: Session = Depends(get_db)):
    """
    Retrieve all feature records.
    """
    return feature_service.get_all_features(db)


@router.get("/{id}", response_model=FeatureResponse)
def get_feature_by_id(id: int, db: Session = Depends(get_db)):
    """
    Retrieve a feature record by its ID.
    """
    feature = feature_service.get_feature_by_id(db, id)
    if not feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feature with ID {id} not found."
        )
    return feature


@router.post(
    "",
    response_model=FeatureResponse,
    status_code=status.HTTP_201_CREATED
)
def create_feature(
    feature_in: FeatureCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new feature record to support validation of database persistence.
    """
    existing = feature_service.get_feature_by_coordinates(
        db, feature_in.latitude, feature_in.longitude
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Feature with these coordinates already exists."
        )
    return feature_service.save_feature(db, feature_in)
