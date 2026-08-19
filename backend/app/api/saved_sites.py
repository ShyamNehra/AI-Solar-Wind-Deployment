from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.database import get_db
from app.models.saved_site import SavedSite
from app.schemas.saved_site import SavedSiteCreate, SavedSiteOut
from app.auth.dependencies import get_current_user
from app.auth.models import User

router = APIRouter()

@router.get("/saved", response_model=List[SavedSiteOut])
def get_saved_sites(
    organization_id: str = Query(..., description="Team workspace organization ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fetch all saved sites strictly isolated for a given team workspace organization_id.
    """
    sites = db.query(SavedSite).filter(SavedSite.organization_id == organization_id).order_by(SavedSite.created_at.desc()).all()
    return sites

@router.post("/saved", response_model=SavedSiteOut, status_code=status.HTTP_201_CREATED)
def create_saved_site(
    payload: SavedSiteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Save a favorite site to the database under the user's team workspace.
    If site at exact lat/lng already exists for this team, update it.
    """
    existing = db.query(SavedSite).filter(
        SavedSite.organization_id == payload.organization_id,
        SavedSite.latitude == payload.latitude,
        SavedSite.longitude == payload.longitude
    ).first()

    if existing:
        existing.name = payload.name
        existing.description = payload.description
        existing.status = payload.status
        existing.score = payload.score
        db.commit()
        db.refresh(existing)
        return existing

    new_site = SavedSite(
        organization_id=payload.organization_id,
        name=payload.name,
        description=payload.description,
        latitude=payload.latitude,
        longitude=payload.longitude,
        status=payload.status,
        score=payload.score
    )
    db.add(new_site)
    db.commit()
    db.refresh(new_site)
    return new_site

@router.delete("/saved/{site_id}")
def delete_saved_site(
    site_id: int,
    organization_id: str = Query(..., description="Team workspace organization ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a saved site from the database strictly within the team workspace.
    """
    site = db.query(SavedSite).filter(
        SavedSite.id == site_id,
        SavedSite.organization_id == organization_id
    ).first()

    if not site:
        raise HTTPException(status_code=404, detail="Saved site not found for this workspace.")

    db.delete(site)
    db.commit()
    return {"message": "Saved site deleted successfully", "id": site_id}
