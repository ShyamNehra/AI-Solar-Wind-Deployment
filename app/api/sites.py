from fastapi import APIRouter

router = APIRouter()


@router.get("/sites", tags=["Sites"])
def get_sites():
    """
    Return the available renewable energy site coordinates.
    """
    return [
        {
            "id": 1,
            "latitude": 19.8135,
            "longitude": 85.8312
        }
    ]
