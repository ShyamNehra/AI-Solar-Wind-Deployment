from fastapi import APIRouter
from app.evaluation.evaluator import evaluate_site

router = APIRouter()


@router.get("/evaluate/{site_id}")
def evaluate(site_id: int):

    # Sample feature values
    features = {
        "latitude": 20.2961,
        "longitude": 85.8245,
        "solar_irradiance": 5.8,
        "wind_speed": 6.2,
        "slope": 2.1,
        "distance_to_grid": 1.8,
        "distance_to_road": 0.45
    }

    return evaluate_site(site_id, features)