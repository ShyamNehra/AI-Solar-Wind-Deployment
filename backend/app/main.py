from fastapi import FastAPI

import app.models.project
import app.models.site
from app.database.database import engine, Base

from app.api.home import router as home_router
from app.api.predictions import router as predictions_router
from app.api.projects import router as projects_router
from app.api.sites import router as sites_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Solar & Wind Deployment Intelligence")

# Include Routers
app.include_router(home_router)
app.include_router(predictions_router)
app.include_router(projects_router, prefix="/projects")
app.include_router(sites_router, prefix="/sites")