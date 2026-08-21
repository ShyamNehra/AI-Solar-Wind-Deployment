from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models.recent_site import RecentSite
from app.schemas.recent_site import RecentSiteCreate, RecentSiteOut
from app.auth.dependencies import get_current_user
from app.auth.models import User

router = APIRouter()

@router.get("/recent", response_model=List[RecentSiteOut])
def get_recent_sites(
    organization_id: str = Query(..., description="Team workspace organization ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fetch the latest 10 recent sites evaluated by all team members in the specified workspace team code.
    """
    sites = db.query(RecentSite).filter(
        RecentSite.organization_id == organization_id
    ).order_by(RecentSite.created_at.desc()).limit(10).all()
    return sites

@router.post("/recent", response_model=RecentSiteOut, status_code=status.HTTP_201_CREATED)
def create_recent_site(
    payload: RecentSiteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Record or update a recent site evaluation for the team workspace.
    """
    existing = db.query(RecentSite).filter(
        RecentSite.organization_id == payload.organization_id,
        RecentSite.latitude == payload.latitude,
        RecentSite.longitude == payload.longitude
    ).first()

    if existing:
        existing.name = payload.name
        existing.status = payload.status
        existing.region = payload.region
        existing.elevation = payload.elevation
        existing.existing_infra = payload.existing_infra
        existing.score = payload.score
        existing.evaluated_by = current_user.username
        db.commit()
        db.refresh(existing)
        return existing

    new_site = RecentSite(
        organization_id=payload.organization_id,
        name=payload.name,
        latitude=payload.latitude,
        longitude=payload.longitude,
        status=payload.status,
        region=payload.region,
        elevation=payload.elevation,
        existing_infra=payload.existing_infra,
        score=payload.score,
        project_id=payload.project_id,
        evaluated_by=current_user.username
    )
    db.add(new_site)
    db.commit()
    db.refresh(new_site)
    return new_site
