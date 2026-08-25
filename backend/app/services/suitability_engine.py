from sqlalchemy.orm import Session
from app.models.site import Site
from app.models.environmental import SiteEnvironmentalData
from app.models.solar_prediction import SolarPrediction
from app.models.wind_prediction import WindPrediction
from app.ml.solar_model import predict_solar_potential
from app.ml.wind_model import predict_wind_potential
from app.services.scoring_engine import calculate_weighted_score, map_score_to_category

SUITABILITY_FORMULA_USED = "Deployment Suitability Score = (Renewable Resource Availability * 0.35) + (Geographic Suitability * 0.25) + (Infrastructure Accessibility * 0.15) + (Environmental Impact * 0.15) + (Economic Feasibility * 0.10)"
SUITABILITY_FORMULA_SOURCE = "Solar & Wind Platform Specification Module 10 (Section 10)"

ENVIRONMENTAL_SCORE_NOTE = (
    "Environmental score is currently computed WITHOUT live Copernicus land cover data, "
    "pending Copernicus integration. Distances to protected zones and water bodies are derived from OSM features."
)

INFRASTRUCTURE_SCORE_NOTE = (
    "nearest_substation_km is currently derived from any OSM power=* tagged node (not specifically "
    "power=substation), and nearest_urban_area_km is derived from place=* nodes (point markers) "
    "rather than landuse polygon boundaries — both are proxies with stated precision limits, "
    "not exact measurements."
)

ECONOMIC_SCORE_NOTE = (
    "Economic Feasibility is proxy-modeled using inverse distance to nearest grid infrastructure "
    "(transmission lines or substations). Closer proximity to grid reduces interconnection capital costs, "
    "representing higher economic feasibility. This is a simplified proxy methodology pending real financial cost data integration."
)

def calculate_site_suitability(site_id: int, db: Session) -> dict:
    """
    Perform a multi-factor suitability analysis for a site.
    Returns calculated sub-scores, overall deployment scores, and explanation notes.
    """
    # 1. Fetch site and environmental data
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise ValueError("Site not found")
        
    env_data = db.query(SiteEnvironmentalData).filter(SiteEnvironmentalData.site_id == site_id).first()
    if not env_data:
        raise ValueError("Environmental data has not been fetched yet. Please refresh environmental data first.")
        
    # 2. Get Solar Potential / Capacity Factor
    solar_pred = db.query(SolarPrediction).filter(SolarPrediction.site_id == site_id).order_by(SolarPrediction.created_at.desc()).first()
    if solar_pred:
        solar_cf = solar_pred.capacity_factor
    elif env_data.average_solar_irradiance is not None:
        # Fallback to dynamic calculation
        res = predict_solar_potential(env_data.average_solar_irradiance)
        solar_cf = res["capacity_factor"]
    else:
        solar_cf = 0.0
        
    # Map Solar Capacity Factor (0.0 to 0.25+) to a 0-100 score
    # Disclosed constant: a capacity factor of 0.25 or above yields 100.0
    solar_resource_score = min(100.0, max(0.0, solar_cf * 400.0))
    
    # 3. Get Wind Potential / Capacity Factor
    wind_pred = db.query(WindPrediction).filter(WindPrediction.site_id == site_id).order_by(WindPrediction.created_at.desc()).first()
    if wind_pred:
        wind_cf = wind_pred.capacity_factor
    elif env_data.average_wind_speed is not None:
        # Fallback to dynamic calculation
        res = predict_wind_potential(env_data.average_wind_speed)
        wind_cf = res["capacity_factor"]
    else:
        wind_cf = 0.0
        
    # Map Wind Capacity Factor (0.0 to 0.50) to a 0-100 score
    # Disclosed constant: a capacity factor of 0.50 yields 100.0
    wind_resource_score = min(100.0, max(0.0, wind_cf * 200.0))
    
    # 4. Geographic Suitability Score (25%)
    # Slope score: steeper slope is penalized
    slope = env_data.average_slope if env_data.average_slope is not None else 0.0
    slope_score = max(0.0, 100.0 - (slope * 4.0))  # slope of 25 degrees or more = 0 score
    
    # Elevation score: high elevation penalized above 2000m
    elevation = env_data.average_elevation if env_data.average_elevation is not None else 0.0
    elevation_score = max(0.0, 100.0 - (max(0.0, elevation - 2000.0) / 10.0))
    
    # Geographic Score is 70% slope, 30% elevation
    geographic_score = round((slope_score * 0.7) + (elevation_score * 0.3), 2)
    
    # 5. Infrastructure Accessibility Score (15%)
    # Road proximity score
    road_km = env_data.nearest_road_km
    if road_km is not None:
        road_score = max(0.0, 100.0 - (road_km * 10.0))  # distance > 10km = 0 score
    else:
        road_score = 0.0  # fallback if no road found within search radius
        
    # Grid proximity score
    substation_km = env_data.nearest_substation_km
    if substation_km is not None:
        grid_score = max(0.0, 100.0 - (substation_km * 5.0))  # distance > 20km = 0 score
    else:
        grid_score = 0.0  # fallback if no power infrastructure found within radius
        
    # Infrastructure Score is 40% road, 60% grid connection
    infrastructure_score = round((road_score * 0.4) + (grid_score * 0.6), 2)
    
    # 6. Environmental Impact Score (15%)
    # Protected zone proximity score
    pz_km = env_data.nearest_protected_zone_km
    if pz_km is not None:
        protected_zone_score = max(0.0, min(100.0, (pz_km / 2.0) * 100.0))  # within 2km is penalized
    else:
        protected_zone_score = 100.0  # no penalty if none found in radius
        
    # Water body proximity score
    wb_km = env_data.nearest_water_body_km
    if wb_km is not None:
        water_body_score = max(0.0, min(100.0, (wb_km / 1.0) * 100.0))  # within 1km is penalized
    else:
        water_body_score = 100.0  # no penalty if none found in radius
        
    # Environmental Score is 50% protected zone, 50% water body
    environmental_score = round((protected_zone_score * 0.5) + (water_body_score * 0.5), 2)
    
    # (Environmental Impact Score calculations done)
    
    # (Infrastructure Score calculations done)
    
    # 7. Economic Feasibility Score (10%)
    # Proxy: Inverse distance to nearest grid connection
    economic_score = round(grid_score, 2)
    
    # 8. Compute final deployment scores
    overall_solar_score = calculate_weighted_score(
        solar_resource_score, geographic_score, infrastructure_score, environmental_score, economic_score
    )
    overall_wind_score = calculate_weighted_score(
        wind_resource_score, geographic_score, infrastructure_score, environmental_score, economic_score
    )
    
    solar_category = map_score_to_category(overall_solar_score)
    wind_category = map_score_to_category(overall_wind_score)
    
    return {
        "site_id": site_id,
        "solar": {
            "resource_score": round(solar_resource_score, 2),
            "geographic_score": geographic_score,
            "infrastructure_score": infrastructure_score,
            "environmental_score": environmental_score,
            "economic_score": economic_score,
            "overall_deployment_score": overall_solar_score,
            "suitability_category": solar_category,
            "capacity_factor": round(solar_cf, 4)
        },
        "wind": {
            "resource_score": round(wind_resource_score, 2),
            "geographic_score": geographic_score,
            "infrastructure_score": infrastructure_score,
            "environmental_score": environmental_score,
            "economic_score": economic_score,
            "overall_deployment_score": overall_wind_score,
            "suitability_category": wind_category,
            "capacity_factor": round(wind_cf, 4)
        },
        "disclosures": {
            "formula_used": SUITABILITY_FORMULA_USED,
            "formula_source": SUITABILITY_FORMULA_SOURCE,
            "economic_score_note": ECONOMIC_SCORE_NOTE,
            "environmental_score_note": ENVIRONMENTAL_SCORE_NOTE,
            "infrastructure_score_note": INFRASTRUCTURE_SCORE_NOTE
        }
    }
