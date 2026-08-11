import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# 1. Database Configuration & Models
from app.database.database import Base, engine
import app.models.project
import app.models.site

# 2. API Router Imports
from app.api.home import router as home_router
from app.api.predictions import router as predictions_router
from app.api.projects import router as projects_router
from app.api.sites import router as sites_router

# 3. Initialize Database Tables
Base.metadata.create_all(bind=engine)

# 4. Fetch Server Configuration from Environment Variables
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

# 5. Initialize FastAPI Application
app = FastAPI(
    title="AI Solar & Wind Deployment Intelligence",
    description="Backend orchestration layer for GIS site suitability, energy estimation, power forecasting, and financial analysis.",
    version="1.0.0",
)

# 6. Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 7. Register API Routers
app.include_router(home_router, tags=["Home"])
app.include_router(predictions_router, prefix="/predictions", tags=["Predictions"])
app.include_router(projects_router, prefix="/projects", tags=["Projects"])
app.include_router(sites_router, prefix="/sites", tags=["Sites"])


# 8. Container & Health Check Endpoint
@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "HEALTHY",
        "service": "AI Solar & Wind Intelligence Engine",
        "version": "1.0.0"
    }


# 9. Direct Execution Entry Point
if __name__ == "__main__":
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=True)