from sqlalchemy.orm import Session
from app.models.project import Project
from app.models.site import Site
from app.models.site_scores import SiteScore
from app.models.deployment_recommendation import DeploymentRecommendation
from app.services.suitability_engine import calculate_site_suitability
from app.services.scoring_engine import calculate_hybrid_score, map_score_to_category

def optimize_project_deployment(project_id: int, db: Session) -> dict:
    """
    Rank all sites within a project, apply technology selection rules,
    recommend installed capacity using NREL land-use density baselines,
    and persist results.
    """
    # 1. Fetch project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise ValueError("Project not found")
        
    sites = db.query(Site).filter(Site.project_id == project_id).all()
    if not sites:
        return {
            "project_id": project_id,
            "ranked_site_ids": [],
            "recommendations": [],
            "capacity_density_solar_source": "NREL PV Land-Use Requirements Study (2013)",
            "capacity_density_wind_source": "NREL Wind Energy Land Use Study (2009)"
        }
        
    recommendations_list = []
    
    # 2. Score each site on the spot if not already scored
    for site in sites:
        score_rec = db.query(SiteScore).filter(SiteScore.site_id == site.id).first()
        if not score_rec:
            try:
                # Dynamically calculate and persist score if missing
                suit = calculate_site_suitability(site.id, db)
                solar_data = suit["solar"]
                wind_data = suit["wind"]
                
                hybrid_score = calculate_hybrid_score(solar_data["overall_deployment_score"], wind_data["overall_deployment_score"])
                hybrid_resource = round((solar_data["resource_score"] * 0.5) + (wind_data["resource_score"] * 0.5), 2)
                hybrid_category = map_score_to_category(hybrid_score)
                
                score_rec = SiteScore(
                    site_id=site.id,
                    solar_score=solar_data["overall_deployment_score"],
                    wind_score=wind_data["overall_deployment_score"],
                    renewable_resource_score=hybrid_resource,
                    geographic_score=solar_data["geographic_score"],
                    infrastructure_score=solar_data["infrastructure_score"],
                    environmental_score=solar_data["environmental_score"],
                    economic_score=solar_data["economic_score"],
                    overall_deployment_score=hybrid_score,
                    suitability_category=hybrid_category,
                    formula_used="overall_deployment_score = (solar_overall_score * 0.5) + (wind_overall_score * 0.5) representing hybrid co-location potential.",
                    formula_source=suit["disclosures"]["formula_source"],
                    economic_score_note=suit["disclosures"]["economic_score_note"],
                    environmental_score_note=suit["disclosures"]["environmental_score_note"],
                    infrastructure_score_note=suit["disclosures"]["infrastructure_score_note"]
                )
                db.add(score_rec)
                db.commit()
                db.refresh(score_rec)
            except Exception as e:
                print(f"Skipping site {site.id} from optimization: {e}", flush=True)
                continue
            
        # 3. Apply technology selection decision rule
        # solar dominant if solar_score > wind_score + 10.0
        # wind dominant if wind_score > solar_score + 10.0
        # else hybrid
        solar_s = score_rec.solar_score
        wind_s = score_rec.wind_score
        
        if solar_s - wind_s > 10.0:
            tech_rec = "solar"
        elif wind_s - solar_s > 10.0:
            tech_rec = "wind"
        else:
            tech_rec = "hybrid"
            
        # 4. Capacity planning using NREL density constants
        # site.land_area is stored in acres (assumed unit due to ambiguity in Phase 1)
        # Convert acres to square meters: 1 acre = 4046.85642 m²
        # Fallback to 5.0 acres if missing
        land_acres = site.land_area if site.land_area is not None else 5.0
        land_m2 = land_acres * 4046.85642
        
        if tech_rec == "solar":
            cap_kw = land_m2 * 0.031
        elif tech_rec == "wind":
            cap_kw = land_m2 * 0.005
        else:  # hybrid
            cap_kw = land_m2 * (0.031 + 0.005)
            
        co_location = (tech_rec == "hybrid") or (solar_s >= 50.0 and wind_s >= 50.0)
        
        recommendations_list.append({
            "site_id": site.id,
            "site_name": site.name,
            "overall_deployment_score": score_rec.overall_deployment_score,
            "solar_score": solar_s,
            "wind_score": wind_s,
            "technology_recommendation": tech_rec,
            "recommended_capacity_kw": round(cap_kw, 2),
            "co_location_viability": co_location
        })
        
    # 5. Sort sites by overall_deployment_score descending (expansion priority)
    recommendations_list.sort(key=lambda x: x["overall_deployment_score"], reverse=True)
    
    # Assign expansion priority ranks
    for priority, rec in enumerate(recommendations_list, start=1):
        rec["expansion_priority"] = priority
        
    ranked_site_ids = [rec["site_id"] for rec in recommendations_list]
    
    # 6. Persist to Postgres database
    rec_record = db.query(DeploymentRecommendation).filter(DeploymentRecommendation.project_id == project_id).first()
    if not rec_record:
        rec_record = DeploymentRecommendation(project_id=project_id)
        db.add(rec_record)
        
    rec_record.ranked_site_ids = ranked_site_ids
    rec_record.recommendations = recommendations_list
    db.commit()
    db.refresh(rec_record)
    
    return {
        "project_id": project_id,
        "ranked_site_ids": ranked_site_ids,
        "recommendations": recommendations_list,
        "capacity_density_solar_source": "Solar Capacity Density = 0.031 kW/m² based on NREL PV Land-Use Requirements Study (2013)",
        "capacity_density_wind_source": "Wind Capacity Density = 0.005 kW/m² based on NREL Wind Energy Land Use Study (2009)"
    }
