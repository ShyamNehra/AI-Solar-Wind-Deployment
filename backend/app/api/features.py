from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.schemas.feature_store import FeatureResponse, FeatureCreate
from app.services.feature_store_services import FeatureStoreService

router = APIRouter(prefix="/features", tags=["Feature Store Engine"])

# Database session dependency injection helper
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=FeatureResponse, status_code=status.HTTP_201_CREATED)
def create_feature_record(payload: FeatureCreate, db: Session = Depends(get_db)):
    """Manually insert an engineered matrix sample row directly into storage columns."""
    # Optional: Run a cache lookup pattern first to prevent duplication
    existing = FeatureStoreService.lookup_cache(db, payload.latitude, payload.longitude)
    if existing:
        raise HTTPException(status_code=400, detail="Calculation profile already exists for these coordinates.")
    return FeatureStoreService.save_features(db, payload)

@router.get("/", response_model=list[FeatureResponse])
def read_all_feature_records(db: Session = Depends(get_db)):
    """Fetch every single cached matrix block currently available in the system."""
    return FeatureStoreService.get_all_features(db)

@router.get("/{id}", response_model=FeatureResponse)
def read_single_feature_record(id: int, db: Session = Depends(get_db)):
    """Locate an isolated feature layout index row directly using its tracking key ID."""
    record = FeatureStoreService.get_feature_by_id(db, id)
    if not record:
        raise HTTPException(status_code=404, detail="Feature tracking reference matrix profile not found.")
    return record