from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.postgres import get_db
from app.models.user import User
from app.models.site import Site
from app.api.dependencies import require_any_role
from app.services.forecasting_engine import (
    generate_seasonal_forecast,
    generate_longterm_projection,
    generate_revenue_forecast
)
from app.schemas.forecasting import (
    SeasonalForecastOut,
    LongTermForecastOut,
    RevenueForecastOut
)

router = APIRouter(prefix="/sites", tags=["Forecasting"])

def verify_site_access(site_id: int, db: Session, current_user: User) -> Site:
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")
        
    project = site.project
    user_roles = [role.name for role in current_user.roles]
    if "Administrator" not in user_roles and project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return site

@router.post("/{site_id}/forecast/seasonal", response_model=SeasonalForecastOut)
def get_seasonal_forecast(
    site_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_role(["Planner", "GIS Analyst", "Project Manager"]))
):
    try:
        verify_site_access(site_id, db, current_user)
        res = generate_seasonal_forecast(site_id, db)
        
        # Trigger forecast refresh completion notification
        from app.models.notification import Notification
        notif = Notification(
            user_id=current_user.id,
            title="Forecast Refresh Complete",
            message=f"Seasonal energy production forecast for Site {site_id} has been refreshed successfully.",
            type="forecast_refresh"
        )
        db.add(notif)
        db.commit()
        
        return res
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Seasonal forecast error: {str(e)}")

@router.post("/{site_id}/forecast/longterm", response_model=LongTermForecastOut)
def get_longterm_forecast(
    site_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_role(["Planner", "GIS Analyst", "Project Manager"]))
):
    try:
        verify_site_access(site_id, db, current_user)
        res = generate_longterm_projection(site_id, db)
        return res
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Longterm forecast error: {str(e)}")

@router.post("/{site_id}/forecast/revenue", response_model=RevenueForecastOut)
def get_revenue_forecast(
    site_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_role(["Planner", "GIS Analyst", "Project Manager"]))
):
    try:
        verify_site_access(site_id, db, current_user)
        res = generate_revenue_forecast(site_id, db)
        return res
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Revenue forecast error: {str(e)}")
