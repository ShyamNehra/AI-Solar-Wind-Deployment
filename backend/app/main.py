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
