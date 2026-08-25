from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.analysis import router as analysis_router

app = FastAPI(
    title="Solar & Wind Deployment Intelligence Platform API",
    description="Backend API for hybrid wind-solar site intelligence assessments.",
    version="1.0.0"
)

# CORS configurations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits requests from localhost:5173 / frontend ports
"""
Solar & Wind Deployment Intelligence Platform - FastAPI Main Application
"""

import os
import logging
from pathlib import Path
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings, BASE_DIR

logger = logging.getLogger("app.main")
logging.basicConfig(level=logging.INFO)

logger.info("Initializing %s v%s", settings.PROJECT_NAME, settings.VERSION)

from app.api.home import router as home_router
from app.api.projects import router as project_router
from app.api.sites import router as site_router
from app.api.predictions import router as prediction_router
from app.api import features
from app.api import solar
from app.api.auth import router as auth_router
from app.api.assessment import router as assessment_router
from app.api.dashboard import router as dashboard_router
from app.api.reports import router as reports_router
from app.api.feature_store import router as feature_store_router
from app.api.pipeline import router as pipeline_router
from app.api.analysis import router as analysis_router
from app.api.forecasting import router as forecasting_router
from app.api.ml import router as ml_router

from app.database.database import engine, Base
from app.models.user import User
from app.models.project import Project
from app.models.site import Site
from app.models.feature import Feature
from app.models.report import Report
from app.models.assessment import Assessment
from app.models.environmental_data import EnvironmentalData
from app.models.solar_prediction import SolarPrediction
from app.models.wind_prediction import WindPrediction
from app.models.feature_store import FeatureStore

app = FastAPI(
    title="Solar & Wind Deployment Intelligence Platform",
    description="AI-powered renewable energy site assessment and deployment intelligence.",
    version="1.0.0"
)

frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")

# Allow all localhost origins so Vite dev server port differences don't block CORS
origins = [
    frontend_url,
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(analysis_router)

@app.get("/")
def home():
    return {"message": "Solar Wind Deployment Intelligence API"}

@app.get("/health")
def health_check():
    return {"status": "Running"}

@app.get("/about")
def about_project():
    return {"project": "Solar & Wind Deployment Intelligence Platform"}
Base.metadata.create_all(bind=engine)

app.include_router(home_router)
app.include_router(auth_router)
app.include_router(project_router)
app.include_router(site_router)
app.include_router(prediction_router)
app.include_router(features.router)
app.include_router(solar.router)
app.include_router(assessment_router)
app.include_router(dashboard_router)
app.include_router(reports_router)
app.include_router(feature_store_router)
app.include_router(pipeline_router)
app.include_router(analysis_router)
app.include_router(forecasting_router)
app.include_router(ml_router)


@app.on_event("startup")
def startup_model_validation():
    """
    Startup validation for ML inference artifacts: verifies best_model.joblib and feature_columns.json.
    """
    models_dir = BASE_DIR / "models"
    best_model_path = models_dir / "best_model.joblib"
    feature_columns_path = models_dir / "feature_columns.json"

    missing = []
    if not best_model_path.exists():
        missing.append("best_model.joblib")
    if not feature_columns_path.exists():
        missing.append("feature_columns.json")

    if missing:
        print(f"WARNING: Startup validation notice - missing required ML artifacts: {', '.join(missing)}. Call POST /ml/train to train and serialize models.")
    else:
        print("✓ Startup ML Validation Passed: best_model.joblib and feature_columns.json verified.")




@app.get("/")
def root():
    return {
        "message": "Solar & Wind Deployment Intelligence Platform API",
        "google_oauth_configured": bool(
            os.getenv("GOOGLE_CLIENT_ID")
            and os.getenv("GOOGLE_CLIENT_SECRET")
        ),
    }

from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.auth.auth_handler import get_db, get_current_user
from app.api.auth import login_for_access_token, register_user, refresh_token
from app.schemas.user import UserCreate

@app.post("/login", tags=["Root Authentication"])
def root_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return login_for_access_token(form_data, db)

@app.post("/register", tags=["Root Authentication"])
def root_register(user_data: UserCreate, db: Session = Depends(get_db)):
    return register_user(user_data, db)

@app.post("/refresh-token", tags=["Root Authentication"])
def root_refresh_token(current_user = Depends(get_current_user)):
    return refresh_token(current_user)

from app.api.auth import get_profile, update_profile
from app.schemas.user import ProfileUpdate

@app.get("/profile", tags=["Root Profile"])
def root_get_profile(current_user = Depends(get_current_user)):
    return get_profile(current_user)

@app.put("/profile", tags=["Root Profile"])
def root_update_profile(profile_data: ProfileUpdate, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    return update_profile(profile_data, current_user, db)
