from fastapi import FastAPI

from app.database.database import Base, engine
from app.models.project import Project  # Import to register model with Base metadata
from app.models.feature import Feature  # Import to register Feature model with Base metadata
from app.api.home import router as home_router
from app.api.projects import router as projects_router
from app.api.sites import router as sites_router
from app.api.predictions import router as predictions_router
from routers.features import router as features_router
from app.api.dashboard import router as dashboard_router
from routers.solar import router as solar_router

from fastapi.staticfiles import StaticFiles

# Create the database tables automatically
Base.metadata.create_all(bind=engine)

# Initialize the FastAPI application with professional metadata
app = FastAPI(
    title="Solar & Wind Deployment Intelligence Platform API",
    description="Backend API for the Solar & Wind Deployment Intelligence Platform",
    version="1.0.0"
)

# Mount static files directory for images
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Register feature routers
app.include_router(home_router)
app.include_router(projects_router)
app.include_router(sites_router)
app.include_router(predictions_router)
app.include_router(features_router)
app.include_router(dashboard_router)
app.include_router(solar_router)


@app.get("/health", tags=["System"])
def health_check():
    """
    Health check endpoint to verify if the FastAPI backend is operational.
    """
    return {"status": "Running"}


@app.get("/about", tags=["Project"])
def about_project():
    """
    About endpoint to identify the project associated with this backend API.
    """
    return {"project": "Solar & Wind Deployment Intelligence Platform"}
