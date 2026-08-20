import os
import sys
import logging
import subprocess
import asyncio
from contextlib import asynccontextmanager
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


def run_db_initialization_and_seed():
    """Create all schema tables and seed default users automatically."""
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized.")

        # Execute seed script
        seed_script = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts", "seed_users.py")
        if not os.path.exists(seed_script):
            seed_script = "scripts/seed_users.py"

        if os.path.exists(seed_script):
            result = subprocess.run([sys.executable, seed_script], capture_output=True, text=True)
            logger.info(f"Database seeding completed: {result.stdout.strip()}")
            if result.stderr:
                logger.warning(f"Database seeding warnings: {result.stderr.strip()}")
    except Exception as e:
        logger.error(f"Error during DB startup initialization/seeding: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run seeding in background to allow immediate port binding
    asyncio.create_task(asyncio.to_thread(run_db_initialization_and_seed))
    yield
    # Cleanup logic (if any) runs on shutdown


# 3. Fetch Server Configuration from Environment Variables
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
raw_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000"
)
ALLOWED_ORIGINS = [origin.strip() for origin in raw_origins.split(",") if origin.strip() and origin.strip() != "*"]

# 4. Initialize FastAPI Application
app = FastAPI(
    title="AI Solar & Wind Deployment Intelligence",
    description="Backend orchestration layer for GIS site suitability, energy estimation, power forecasting, and financial analysis.",
    version="1.0.0",
    lifespan=lifespan
)

# 5. Configure Spec-Compliant CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"^https?:\/\/.*",  # Permissive origin matching compatible with credentials
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 6. Attach Rate Limiter & Security Middlewares
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SecurityHeadersMiddleware)

# 7. Container & Health Check Endpoints (Supports both GET and HEAD for Render probes)
@app.api_route("/health", methods=["GET", "HEAD"], tags=["Health"])
@app.api_route("/", methods=["GET", "HEAD"], include_in_schema=False)
def health_check():
    return {
        "status": "HEALTHY",
        "service": "AI Solar & Wind Intelligence Engine",
        "version": "1.0.0"
    }

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


# 10. Direct Execution Entry Point
if __name__ == "__main__":
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=True)