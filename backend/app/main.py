import os
import logging
import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.rate_limiter import limiter
from app.core.security_middleware import SecurityHeadersMiddleware
from app.auth.router import router as auth_router

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("security")

# 1. Database Configuration & Models
from app.database.database import Base, engine
import app.models  # Imports all database ORM models

# 2. API Router Imports
from app.api.home import router as home_router
from app.api.predictions import router as predictions_router
from app.api.projects import router as projects_router
from app.api.sites import router as sites_router
from app.api.saved_sites import router as saved_sites_router

# 3. Initialize Database Tables
Base.metadata.create_all(bind=engine)

# 4. Fetch Server Configuration from Environment Variables
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
ALLOWED_ORIGINS = [
    origin.strip() for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000"
    ).split(",") if origin.strip()
]

# 5. Initialize FastAPI Application
app = FastAPI(
    title="AI Solar & Wind Deployment Intelligence",
    description="Backend orchestration layer for GIS site suitability, energy estimation, power forecasting, and financial analysis.",
    version="1.0.0",
)

# 6. Attach Rate Limiter & Security Middlewares
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SecurityHeadersMiddleware)

# 7. Configure Restricted CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Requested-With"],
)

# 8. Register API Routers
app.include_router(home_router, tags=["Home"])
app.include_router(predictions_router, prefix="/predictions", tags=["Predictions"])
app.include_router(projects_router, prefix="/projects", tags=["Projects"])
app.include_router(sites_router, prefix="/sites", tags=["Sites"])
app.include_router(saved_sites_router, prefix="/sites", tags=["Saved Sites"])
app.include_router(auth_router)


# 9. Global Exception Handler to sanitize 500 errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error processing request {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Request logged for safety compliance."}
    )


# 10. Container & Health Check Endpoint
@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "HEALTHY",
        "service": "AI Solar & Wind Intelligence Engine",
        "version": "1.0.0"
    }


# 11. Direct Execution Entry Point
if __name__ == "__main__":
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=True)