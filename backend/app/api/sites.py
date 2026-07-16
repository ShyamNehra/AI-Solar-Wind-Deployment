from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.site import Site
from app.schemas.site import SiteCreateSchema

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_site(payload: SiteCreateSchema, db: Session = Depends(get_db)):
    new_site = Site(
        project_id=payload.project_id,
        latitude=payload.latitude,
        longitude=payload.longitude,
        area_sq_meters=payload.area_sq_meters
    )
    db.add(new_site)
    db.commit()
    db.refresh(new_site)
    return {"message": "Site registered successfully", "data": new_site}

@router.get("/")
def get_sites(db: Session = Depends(get_db)):
    sites = db.query(Site).all()
    return {"total_sites": len(sites), "sites": sites}