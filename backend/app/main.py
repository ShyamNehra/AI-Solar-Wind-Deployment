from fastapi import FastAPI

from app.api.home import router as home_router
from app.api.predictions import router as predictions_router
from app.api.projects import router as projects_router
from app.api.sites import router as sites_router

import app.models.project
import app.models.site
from app.database.database import engine, Base
from app.api import predictions


Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(predictions.router)
app.include_router(home_router)
app.include_router(predictions_router)
app.include_router(projects_router, prefix="/projects")
app.include_router(sites_router, prefix="/sites")


