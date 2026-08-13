import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.site import Site
from app.models.suitability_score import SuitabilityScore
from app.services.environmental import fetch_nasa_data, fetch_osm_grid_distance
from app.services.ai_engine import generate_ai_risk_analysis

# Router prefix is relative because main.py already attaches settings.API_V1_STR ("/api/v1")
router = APIRouter(prefix="/analytics", tags=["Analytics & Scoring"])


@router.post("/evaluate/{site_id}")
def run_site_evaluation(site_id: str, db: Session = Depends(get_db)):
    # 1. Fetch site coordinates
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    # 2. Fetch live data from NASA POWER and OpenStreetMap
    nasa_data = fetch_nasa_data(site.latitude, site.longitude)
    dist_to_grid_km = fetch_osm_grid_distance(site.latitude, site.longitude)

    # 3. Calculate scores (0-100 scale)
    solar_score = round(min((nasa_data["solar_irradiance"] / 6.0) * 100, 100), 2)
    wind_score = round(min((nasa_data["wind_speed"] / 10.0) * 100, 100), 2)
    infrastructure_score = max(round(100 - (dist_to_grid_km * 2), 2), 0.0)

    # Weighted Scoring Formula (Module 10)
    resource_score = max(solar_score, wind_score)
    overall_score = round(
        (0.35 * resource_score) +
        (0.25 * 80.0) +                  # Geographic
        (0.15 * infrastructure_score) +  # Infrastructure
        (0.15 * 85.0) +                  # Environmental
        (0.10 * 75.0), 2                 # Economic
    )

    # 4. Generate AI Risks and Recommendations using Gemini
    ai_insights = generate_ai_risk_analysis(
        solar_score=solar_score,
        wind_score=wind_score,
        infrastructure_score=infrastructure_score,
        overall_score=overall_score
    )

    # 5. Persist or Update database record
    score_record = db.query(SuitabilityScore).filter(SuitabilityScore.site_id == site_id).first()
    if not score_record:
        score_record = SuitabilityScore(site_id=site_id)
        db.add(score_record)

    score_record.overall_score = overall_score
    score_record.solar_score = solar_score
    score_record.wind_score = wind_score
    score_record.resource_score = resource_score
    score_record.infrastructure_score = infrastructure_score
    score_record.recommendation = ai_insights.get("recommendation")
    score_record.risks_json = json.dumps(ai_insights.get("risks", []))

    db.commit()
    db.refresh(score_record)

    return {
        "id": score_record.id,
        "site_id": score_record.site_id,
        "overall_score": score_record.overall_score,
        "solar_score": score_record.solar_score,
        "wind_score": score_record.wind_score,
        "infrastructure_score": score_record.infrastructure_score,
        "recommendation": score_record.recommendation,
        "risks": json.loads(score_record.risks_json),
        "created_at": score_record.created_at
    }