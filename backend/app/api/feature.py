from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.feature import Feature
from app.schemas.feature import FeatureCreate, FeatureResponse
from app.services.feature_store import FeatureStoreService

router = APIRouter()

# Create FeatureStoreService object
feature_service = FeatureStoreService()


# Database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# POST /features
@router.post("/features", response_model=FeatureResponse)
def create_feature(
    feature: FeatureCreate,
    db: Session = Depends(get_db)
):
    return feature_service.save_feature(db, feature)


# GET /features
@router.get("/features", response_model=list[FeatureResponse])
def get_features(db: Session = Depends(get_db)):
    return db.query(Feature).all()


# GET /features/{id}
@router.get("/features/{id}", response_model=FeatureResponse)
def get_feature(id: int, db: Session = Depends(get_db)):
    feature = db.query(Feature).filter(Feature.id == id).first()

    if feature is None:
        raise HTTPException(status_code=404, detail="Feature not found")

    return feature