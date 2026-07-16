from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def home():
    return {
        "message": "Solar & Wind Deployment Intelligence Platform"
    }

@router.get("/about")
def get_about():
    return{
        "project": "solar and wind deployment project"
    }

@router.get("/health")
def get_health():
    return{
        "status": "running"
    }