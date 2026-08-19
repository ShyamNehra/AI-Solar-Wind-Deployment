from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.postgres import get_db
from app.models.user import User
from app.api.dependencies import get_current_user, require_any_role
from app.services.suitability_engine import calculate_site_suitability
from app.schemas.suitability import SuitabilityOut

router = APIRouter(prefix="/sites", tags=["Suitability"])

@router.post("/{site_id}/suitability", response_model=SuitabilityOut)
def get_site_suitability(
    site_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_role(["Planner", "GIS Analyst", "Project Manager"]))
):
    """
    Execute multi-factor suitability analysis for the given site, returning the breakdowns for both solar and wind.
    """
    try:
        suitability_data = calculate_site_suitability(site_id, db)
        return suitability_data
    except ValueError as e:
        msg = str(e)
        if "not found" in msg.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Suitability error: {str(e)}")
