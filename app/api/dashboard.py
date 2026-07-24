from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["UI"])


@router.get("/dashboard", response_class=HTMLResponse)
def get_dashboard():
    """
    Serve the premium Solar & Wind Deployment Intelligence Platform Dashboard UI.
    """
    with open("app/templates/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)
