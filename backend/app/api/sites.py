from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.database import get_db
from app.models.project import Project
from app.models.site import Site
from app.models.user import User
from app.schemas.site import SiteCreate, SiteResponse

router = APIRouter(prefix="/sites", tags=["Sites"])


@router.post("/", response_model=SiteResponse, status_code=status.HTTP_201_CREATED)
def register_site(
    site_in: SiteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Register a new site under a project."""
    # Verify parent project exists and belongs to current user
    project = db.query(Project).filter(Project.id == site_in.project_id, Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Parent project not found or access denied")

    new_site = Site(
        project_id=site_in.project_id,
        name=site_in.name,
        latitude=site_in.latitude,
        longitude=site_in.longitude,
        region=site_in.region,
        land_area_sqkm=site_in.land_area_sqkm,
        elevation_m=site_in.elevation_m,
        land_ownership=site_in.land_ownership
    )
    db.add(new_site)
    db.commit()
    db.refresh(new_site)
    return new_site


@router.get("/project/{project_id}", response_model=list[SiteResponse])
def list_sites_by_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve all sites associated with a given project."""
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return db.query(Site).filter(Site.project_id == project_id).all()