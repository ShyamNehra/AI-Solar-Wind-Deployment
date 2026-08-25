from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.postgres import get_db
from app.api.dependencies import require_role
from app.models.user import User
from app.models.project import Project
from app.models.site import Site
from app.models.solar_prediction import SolarPrediction
from app.models.wind_prediction import WindPrediction
from app.models.energy_forecast import EnergyForecast
from app.services.suitability_engine import (
    ENVIRONMENTAL_SCORE_NOTE,
    INFRASTRUCTURE_SCORE_NOTE,
    ECONOMIC_SCORE_NOTE
)
from app.api.predictions import (
    WIND_CAP_FACTOR_NOTE
)
from app.services.forecasting_engine import (
    GRID_CONTRIBUTION_NOTE,
    ELECTRICITY_RATE_SOURCE
)

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/data-sources")
def get_admin_data_sources(current_user: User = Depends(require_role("Administrator"))):
    return [
        {
            "key": "wind_capacity_factor",
            "label": "Wind capacity factor",
            "disclosure": WIND_CAP_FACTOR_NOTE,
            "status": "placeholder pending real turbine power curves"
        },
        {
            "key": "economic_feasibility",
            "label": "Economic Feasibility sub-score",
            "disclosure": ECONOMIC_SCORE_NOTE,
            "status": "placeholder pending real financial/cost data"
        },
        {
            "key": "environmental_impact",
            "label": "Environmental Impact sub-score",
            "disclosure": ENVIRONMENTAL_SCORE_NOTE,
            "status": "OPEN blocker, PENDING_COPERNICUS_AUTH"
        },
        {
            "key": "grid_contribution",
            "label": "Grid contribution ratio",
            "disclosure": GRID_CONTRIBUTION_NOTE,
            "status": "placeholder pending real regional demand data"
        },
        {
            "key": "electricity_price",
            "label": "Electricity price",
            "disclosure": ELECTRICITY_RATE_SOURCE,
            "status": "placeholder, real source but generic figure"
        },
        {
            "key": "land_use_density",
            "label": "Land-use capacity densities",
            "disclosure": "Solar Capacity Density = 0.031 kW/m² based on NREL PV Land-Use Requirements Study (2013); Wind Capacity Density = 0.005 kW/m² based on NREL Wind Energy Land Use Study (2009)",
            "status": "real source, generalized applicability"
        },
        {
            "key": "infrastructure_proximity",
            "label": "Infrastructure proximity",
            "disclosure": INFRASTRUCTURE_SCORE_NOTE,
            "status": "real live data, stated precision limits"
        }
    ]

@router.get("/users")
def get_admin_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Administrator"))
):
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "roles": [r.name for r in u.roles],
            "is_active": u.is_active
        }
        for u in users
    ]

@router.get("/platform-analytics")
def get_platform_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Administrator"))
):
    total_users = db.query(User).count()
    total_projects = db.query(Project).count()
    total_sites = db.query(Site).count()
    total_predictions_solar = db.query(SolarPrediction).count()
    total_predictions_wind = db.query(WindPrediction).count()
    total_forecasts = db.query(EnergyForecast).count()
    
    return {
        "total_users": total_users,
        "total_projects": total_projects,
        "total_sites": total_sites,
        "total_predictions_solar": total_predictions_solar,
        "total_predictions_wind": total_predictions_wind,
        "total_forecasts": total_forecasts,
        "system_status": "healthy"
    }
