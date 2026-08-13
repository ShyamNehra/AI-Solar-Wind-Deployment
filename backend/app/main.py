from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from dotenv import load_dotenv  # <--- ADD THIS

load_dotenv()  # <--- ADD THIS (Loads .env into os.environ)

from app.database.database import engine, Base, get_db
from app.utils.config import settings
from app.api import auth, projects, sites, environmental, analytics

import app.models  # noqa: F401

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

# Include Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(projects.router, prefix=settings.API_V1_STR)
app.include_router(sites.router, prefix=settings.API_V1_STR)
app.include_router(environmental.router, prefix=settings.API_V1_STR)
app.include_router(analytics.router, prefix=settings.API_V1_STR)


@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} API"}


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT current_database();")).fetchone()
        return {
            "status": "Running",
            "database_status": "Connected",
            "active_database": result[0] if result else None
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database connection failed: {str(e)}"
        )