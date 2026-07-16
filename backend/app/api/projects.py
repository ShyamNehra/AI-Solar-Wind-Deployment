from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Absolute package imports matching your backend workspace path
from app.database.database import get_db
from app.models.project import Project
from app.schemas.project import ProjectCreateSchema

router = APIRouter()

# 1. Create Project Endpoint (POST)
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreateSchema, db: Session = Depends(get_db)):
    # Map incoming schema data to your physical database column template
    new_project = Project(
        project_name=payload.project_name,
        description=payload.description,
        state=payload.state,
        latitude=payload.latitude,
        longitude=payload.longitude
    )
    
    # Commit transaction to PostgreSQL
    db.add(new_project)
    db.commit()
    db.refresh(new_project) # Refreshes object to grab the auto-generated ID
    
    return {
        "message": "Project created successfully",
        "data": new_project
    }

# 2. Retrieve All Projects Endpoint (GET)
@router.get("/")
def get_projects(db: Session = Depends(get_db)):
    # Run a live select query against your table
    projects = db.query(Project).all()
    
    return {
        "total_projects": len(projects),
        "projects": projects
    }