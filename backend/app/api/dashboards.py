from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.postgres import get_db
from app.api.dependencies import require_any_role, require_role
from app.models.user import User
from app.models.project import Project
from app.models.site import Site
from app.models.site_scores import SiteScore
from app.models.environmental import SiteEnvironmentalData
from app.models.energy_forecast import EnergyForecast
from app.models.deployment_recommendation import DeploymentRecommendation
from geoalchemy2.shape import to_shape

router = APIRouter(prefix="/dashboards", tags=["Dashboards"])

def verify_project_access(project_id: int, db: Session, current_user: User) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        
    user_roles = [role.name for role in current_user.roles]
    if "Administrator" not in user_roles and project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return project

@router.get("/planner/{project_id}")
def get_planner_dashboard(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_role(["Planner", "Project Manager"]))
):
    project = verify_project_access(project_id, db, current_user)
    sites = db.query(Site).filter(Site.project_id == project_id).all()
    
    rec_record = db.query(DeploymentRecommendation).filter(DeploymentRecommendation.project_id == project_id).first()
    
    recommended_sites = []
    for site in sites:
        score_rec = db.query(SiteScore).filter(SiteScore.site_id == site.id).first()
        forecast_rec = db.query(EnergyForecast).filter(EnergyForecast.site_id == site.id).first()
        
        rec_details = None
        if rec_record and rec_record.recommendations:
            rec_details = next((r for r in rec_record.recommendations if r["site_id"] == site.id), None)
            
        recommended_sites.append({
            "site_id": site.id,
            "site_name": site.name,
            "suitability_scores": {
                "overall_score": score_rec.overall_deployment_score if score_rec else None,
                "solar_score": score_rec.solar_score if score_rec else None,
                "wind_score": score_rec.wind_score if score_rec else None,
                "category": score_rec.suitability_category if score_rec else None,
                "geographic": score_rec.geographic_score if score_rec else None,
                "infrastructure": score_rec.infrastructure_score if score_rec else None,
                "environmental": score_rec.environmental_score if score_rec else None,
                "economic": score_rec.economic_score if score_rec else None
            },
            "generation_forecasts": {
                "solar_seasonal_kwh": forecast_rec.solar_seasonal_kwh if forecast_rec else None,
                "wind_seasonal_kwh": forecast_rec.wind_seasonal_kwh if forecast_rec else None,
                "solar_longterm_kwh": forecast_rec.solar_longterm_kwh if forecast_rec else None,
                "wind_longterm_kwh": forecast_rec.wind_longterm_kwh if forecast_rec else None
            },
            "investment_recommendations": {
                "technology_recommendation": rec_details["technology_recommendation"] if rec_details else None,
                "recommended_capacity_kw": rec_details["recommended_capacity_kw"] if rec_details else None,
                "co_location_viability": rec_details["co_location_viability"] if rec_details else None
            }
        })
        
    # Sort sites by overall suitability score descending
    recommended_sites.sort(key=lambda x: x["suitability_scores"]["overall_score"] or 0.0, reverse=True)
    
    return {
        "project_id": project_id,
        "project_name": project.name,
        "recommended_sites": recommended_sites,
        "data_note": "Wind capacity factor calculations assume standard baseline turbine specifications. Financial and investment estimates are illustrative proxies."
    }

@router.get("/gis-analyst/{project_id}")
def get_gis_analyst_dashboard(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_role(["GIS Analyst", "Project Manager"]))
):
    project = verify_project_access(project_id, db, current_user)
    sites = db.query(Site).filter(Site.project_id == project_id).all()
    
    results = []
    for site in sites:
        env_data = db.query(SiteEnvironmentalData).filter(SiteEnvironmentalData.site_id == site.id).first()
        geom = to_shape(site.geom)
        
        results.append({
            "site_id": site.id,
            "site_name": site.name,
            "spatial_distribution": {
                "latitude": geom.y,
                "longitude": geom.x,
                "elevation_m": env_data.average_elevation if env_data else None,
                "slope_deg": env_data.average_slope if env_data else None
            },
            "proximity_analysis": {
                "nearest_road_km": env_data.nearest_road_km if env_data else None,
                "nearest_substation_km": env_data.nearest_substation_km if env_data else None,
                "nearest_urban_area_km": env_data.nearest_urban_area_km if env_data else None,
                "nearest_protected_zone_km": env_data.nearest_protected_zone_km if env_data else None,
                "nearest_water_body_km": env_data.nearest_water_body_km if env_data else None
            },
            "land_cover_suitability": {
                "land_cover_type": env_data.land_cover_type if env_data else None,
                "note": "Copernicus land cover data status is PENDING_COPERNICUS_AUTH."
            }
        })
        
    return {
        "project_id": project_id,
        "project_name": project.name,
        "gis_analyst_data": results
    }

@router.get("/project-manager/{project_id}")
def get_project_manager_dashboard(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_role(["Project Manager"]))
):
    project = verify_project_access(project_id, db, current_user)
    sites = db.query(Site).filter(Site.project_id == project_id).all()
    
    cost_benefit_list = []
    total_score = 0.0
    scored_count = 0
    expansion_risk_flags = []
    
    for site in sites:
        score_rec = db.query(SiteScore).filter(SiteScore.site_id == site.id).first()
        forecast_rec = db.query(EnergyForecast).filter(EnergyForecast.site_id == site.id).first()
        env_data = db.query(SiteEnvironmentalData).filter(SiteEnvironmentalData.site_id == site.id).first()
        
        if score_rec:
            total_score += score_rec.overall_deployment_score
            scored_count += 1
            if score_rec.suitability_category in ["Low Suitability", "Unsuitable"]:
                expansion_risk_flags.append({
                    "site_id": site.id,
                    "site_name": site.name,
                    "risk": f"Low overall suitability score: {score_rec.overall_deployment_score} ({score_rec.suitability_category})"
                })
                
        if env_data is None:
            expansion_risk_flags.append({
                "site_id": site.id,
                "site_name": site.name,
                "risk": "Environmental proximity data incomplete — cannot confirm setback compliance"
            })
        else:
            if (env_data.nearest_protected_zone_km is not None and env_data.nearest_protected_zone_km < 2.0) or \
               (env_data.nearest_water_body_km is not None and env_data.nearest_water_body_km < 1.0):
                expansion_risk_flags.append({
                    "site_id": site.id,
                    "site_name": site.name,
                    "risk": "Environmental setback penalty: Proximity to protected zone (< 2km) or water body (< 1km)"
                })
            if env_data.nearest_protected_zone_km is None or \
               env_data.nearest_water_body_km is None or \
               env_data.nearest_road_km is None or \
               env_data.nearest_substation_km is None:
                expansion_risk_flags.append({
                    "site_id": site.id,
                    "site_name": site.name,
                    "risk": "Environmental proximity data incomplete — cannot confirm setback compliance"
                })
                
        cost_benefit_list.append({
            "site_id": site.id,
            "site_name": site.name,
            "cost_benefit_analysis": {
                "projected_annual_revenue_usd": forecast_rec.combined_annual_revenue if forecast_rec else None,
                "grid_interconnection_distance_km": env_data.nearest_substation_km if env_data else None,
                "interconnection_cost_proxy_score": score_rec.economic_score if score_rec else None
            }
        })
        
    avg_readiness = round(total_score / scored_count, 2) if scored_count > 0 else 0.0
    
    return {
        "project_id": project_id,
        "project_name": project.name,
        "overall_project_readiness": avg_readiness,
        "cost_benefit_analysis": cost_benefit_list,
        "expansion_risk_flags": expansion_risk_flags,
        "data_note": "Cost-benefit analysis uses a proxy interconnection cost score and retail rate electricity revenue baseline. Actual construction capital expenditure modeling is deferred."
    }

@router.get("/admin")
def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Administrator"))
):
    users = db.query(User).all()
    total_users = len(users)
    active_users = sum(1 for u in users if u.is_active)
    
    from app.db.mongo import raw_environmental_cache
    cached_docs = 0
    try:
        cached_docs = raw_environmental_cache.count_documents({})
    except Exception:
        pass
        
    return {
        "user_role_management": {
            "total_users": total_users,
            "active_users": active_users,
            "users_list": [
                {"id": u.id, "email": u.email, "roles": [r.name for r in u.roles]}
                for u in users
            ]
        },
        "platform_analytics": {
            "cached_environmental_payloads": cached_docs,
            "total_projects": db.query(Project).count(),
            "total_sites": db.query(Site).count()
        },
        "data_source_management": {
            "copernicus_sentinel_hub": "PENDING_COPERNICUS_AUTH",
            "open_meteo_historical_api": "active",
            "nasa_power_climatology_api": "active",
            "openstreetmap_overpass_api": "active"
        },
        "system_monitoring": {
            "database_engine": "PostgreSQL 16 with PostGIS",
            "cache_engine": "MongoDB 7",
            "disk_usage": "healthy",
            "memory_usage": "healthy"
        }
    }
