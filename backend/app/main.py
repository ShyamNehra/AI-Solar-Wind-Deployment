from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.api.projects import router as projects_router
from app.api.sites import router as sites_router
from app.api.environmental import router as environmental_router
from app.api.predictions import router as predictions_router
from app.api.suitability import router as suitability_router
from app.api.scoring import router as scoring_router
from app.api.forecasting import router as forecasting_router
from app.api.optimization import router as optimization_router
from app.api.admin import router as admin_router
from app.api.dashboards import router as dashboards_router
from app.api.notifications import router as notifications_router
from app.api.reports import router as reports_router
from app.db.mongo import init_mongo
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup Mongo indexes on startup
    init_mongo()
    yield

app = FastAPI(
    title="Solar & Wind Deployment Intelligence Platform API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router, prefix="/api")
app.include_router(projects_router, prefix="/api")
app.include_router(sites_router, prefix="/api")
app.include_router(environmental_router, prefix="/api")
app.include_router(predictions_router, prefix="/api")
app.include_router(suitability_router, prefix="/api")
app.include_router(scoring_router, prefix="/api")
app.include_router(forecasting_router, prefix="/api")
app.include_router(optimization_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(dashboards_router, prefix="/api")
app.include_router(notifications_router, prefix="/api")
app.include_router(reports_router, prefix="/api")

@app.get("/health")
def health():
    return {"status": "healthy"}
