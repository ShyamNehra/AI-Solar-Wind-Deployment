from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.postgres import get_db
from app.models.user import User
from app.models.site_scores import SiteScore
from app.models.solar_prediction import SolarPrediction
from app.models.wind_prediction import WindPrediction
from app.api.dependencies import get_current_user, require_any_role
from app.services.suitability_engine import calculate_site_suitability
from app.services.scoring_engine import calculate_hybrid_score, map_score_to_category
from app.schemas.scoring import SiteScoreOut

router = APIRouter(prefix="/sites", tags=["Scoring"])

@router.post("/{site_id}/score", response_model=SiteScoreOut)
def get_and_persist_site_score(
    site_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_role(["Planner", "GIS Analyst", "Project Manager"]))
):
    """
    Calculate, persist, and return the deployment suitability scores for the given site.
    """
    try:
        # 1. Run suitability calculation
        suit = calculate_site_suitability(site_id, db)
        
        # 2. Get solar and wind overall scores
        solar_data = suit["solar"]
        wind_data = suit["wind"]
        
        # Calculate hybrid overall score and hybrid resource score
        hybrid_score = calculate_hybrid_score(solar_data["overall_deployment_score"], wind_data["overall_deployment_score"])
        hybrid_resource = round((solar_data["resource_score"] * 0.5) + (wind_data["resource_score"] * 0.5), 2)
        hybrid_category = map_score_to_category(hybrid_score)
        
        # 3. Retrieve or create SiteScore db record
        score_record = db.query(SiteScore).filter(SiteScore.site_id == site_id).first()
        if not score_record:
            score_record = SiteScore(site_id=site_id)
            db.add(score_record)
            
        # Update attributes
        score_record.solar_score = solar_data["overall_deployment_score"]
        score_record.wind_score = wind_data["overall_deployment_score"]
        score_record.renewable_resource_score = hybrid_resource
        score_record.geographic_score = solar_data["geographic_score"]
        score_record.infrastructure_score = solar_data["infrastructure_score"]
        score_record.environmental_score = solar_data["environmental_score"]
        score_record.economic_score = solar_data["economic_score"]
        score_record.overall_deployment_score = hybrid_score
        score_record.suitability_category = hybrid_category
        
        # Disclose hybrid formula
        hybrid_formula = (
            "overall_deployment_score = (solar_overall_score * 0.5) + (wind_overall_score * 0.5) "
            "representing co-location hybrid potential, where each technology score is "
            "computed using the 10-factor weighted model."
        )
        score_record.formula_used = hybrid_formula
        score_record.formula_source = suit["disclosures"]["formula_source"]
        score_record.economic_score_note = suit["disclosures"]["economic_score_note"]
        score_record.environmental_score_note = suit["disclosures"]["environmental_score_note"]
        score_record.infrastructure_score_note = suit["disclosures"]["infrastructure_score_note"]
        
        # Commit to Postgres database
        db.commit()
        db.refresh(score_record)
        
        # Trigger low suitability alert if score falls under Low Suitability or Unsuitable
        if score_record.suitability_category in ["Low Suitability", "Unsuitable"]:
            from app.models.notification import Notification
            notif = Notification(
                user_id=current_user.id,
                title="Low Suitability Alert",
                message=f"Site {site_id} has been scored with low suitability: {score_record.overall_deployment_score} ({score_record.suitability_category}).",
                type="low_suitability"
            )
            db.add(notif)
            db.commit()
            
        return score_record
    except ValueError as e:
        msg = str(e)
        if "not found" in msg.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Scoring error: {str(e)}")
