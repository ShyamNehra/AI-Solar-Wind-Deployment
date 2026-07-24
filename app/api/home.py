from fastapi import APIRouter

router = APIRouter()


@router.get("/", tags=["General"])
def read_root():
    """
    Root endpoint that provides a welcoming message for the platform.
    """
    return {
        "message": "Welcome to Solar & Wind Deployment Intelligence Platform"
    }
