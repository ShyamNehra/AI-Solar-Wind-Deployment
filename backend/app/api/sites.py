from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
import math
from app.db.postgres import get_db
from app.models.project import Project
from app.models.site import Site
from app.models.user import User
from app.schemas.site import SiteCreate, SiteOut, SiteCompareOut
from app.api.dependencies import get_current_user
from geoalchemy2.shape import to_shape

router = APIRouter(prefix="/projects/{project_id}/sites", tags=["Sites"])

def haversine_distance(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    # Earth radius in kilometers
    R = 6371.0
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

@router.post("", response_model=SiteOut, status_code=status.HTTP_201_CREATED)
def create_site(
    project_id: int,
    site_in: SiteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        
    user_roles = [role.name for role in current_user.roles]
    if "Administrator" not in user_roles and project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
    # Store coordinates in GeoAlchemy2 Geometry POINT format using WGS84 (SRID 4326)
    wkt_geom = f"SRID=4326;POINT({site_in.longitude} {site_in.latitude})"
    
    site = Site(
        project_id=project_id,
        name=site_in.name,
        geom=wkt_geom,
        land_area=site_in.land_area,
        elevation=site_in.elevation,
        existing_infrastructure=site_in.existing_infrastructure,
        land_ownership=site_in.land_ownership
    )
    db.add(site)
    db.commit()
    db.refresh(site)
    
    return SiteOut(
        id=site.id,
        project_id=site.project_id,
        name=site.name,
        latitude=site_in.latitude,
        longitude=site_in.longitude,
        land_area=site.land_area,
        elevation=site.elevation,
        existing_infrastructure=site.existing_infrastructure,
        land_ownership=site.land_ownership,
        created_at=site.created_at
    )

@router.get("", response_model=List[SiteOut])
def list_sites(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        
    user_roles = [role.name for role in current_user.roles]
    if "Administrator" not in user_roles and project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
    sites = db.query(Site).filter(Site.project_id == project_id).all()
    
    res = []
    for site in sites:
        point = to_shape(site.geom)
        res.append(SiteOut(
            id=site.id,
            project_id=site.project_id,
            name=site.name,
            latitude=point.y,
            longitude=point.x,
            land_area=site.land_area,
            elevation=site.elevation,
            existing_infrastructure=site.existing_infrastructure,
            land_ownership=site.land_ownership,
            created_at=site.created_at
        ))
    return res

@router.get("/compare", response_model=SiteCompareOut)
def compare_sites(
    project_id: int,
    ids: str = Query(..., description="Comma separated site IDs to compare (exactly 2 IDs required)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        
    user_roles = [role.name for role in current_user.roles]
    if "Administrator" not in user_roles and project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
    try:
        site_ids = [int(i) for i in ids.split(",")]
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid site IDs format")
        
    if len(site_ids) != 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Must provide exactly 2 site IDs to compare")
        
    site1 = db.query(Site).filter(Site.id == site_ids[0], Site.project_id == project_id).first()
    site2 = db.query(Site).filter(Site.id == site_ids[1], Site.project_id == project_id).first()
    
    if not site1 or not site2:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One or both sites not found in this project")
        
    p1 = to_shape(site1.geom)
    p2 = to_shape(site2.geom)
    
    s1_out = SiteOut(
        id=site1.id,
        project_id=site1.project_id,
        name=site1.name,
        latitude=p1.y,
        longitude=p1.x,
        land_area=site1.land_area,
        elevation=site1.elevation,
        existing_infrastructure=site1.existing_infrastructure,
        land_ownership=site1.land_ownership,
        created_at=site1.created_at
    )
    
    s2_out = SiteOut(
        id=site2.id,
        project_id=site2.project_id,
        name=site2.name,
        latitude=p2.y,
        longitude=p2.x,
        land_area=site2.land_area,
        elevation=site2.elevation,
        existing_infrastructure=site2.existing_infrastructure,
        land_ownership=site2.land_ownership,
        created_at=site2.created_at
    )
    
    elevation_diff = abs((site1.elevation or 0.0) - (site2.elevation or 0.0))
    distance = haversine_distance(p1.x, p1.y, p2.x, p2.y)
    
    return SiteCompareOut(
        site1=s1_out,
        site2=s2_out,
        elevation_difference=elevation_diff,
        distance_km=distance
    )
from fastapi import APIRouter

router = APIRouter()

@router.get("/sites")
def get_sites():
    return [
        {
            "id": 1,
            "latitude": 19.8135,
            "longitude": 85.8312
        }
    ]
