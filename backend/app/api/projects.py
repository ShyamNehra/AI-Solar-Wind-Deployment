from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.project import Project
from app.schemas.project import ProjectCreate

router = APIRouter()


@router.get("/projects")
def get_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    return projects


@router.post("/projects")
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    new_project = Project(
        project_name=project.project_name,
        description=project.description,
        state=project.state,
        latitude=project.latitude,
        longitude=project.longitude,
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return new_project