from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.postgres import get_db
from app.models.user import User
from app.models.project import Project
from app.api.dependencies import require_any_role
from app.services.optimization_engine import optimize_project_deployment
from app.schemas.optimization import OptimizationOut

router = APIRouter(prefix="/projects", tags=["Optimization"])

def verify_project_access(project_id: int, db: Session, current_user: User) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        
    user_roles = [role.name for role in current_user.roles]
    if "Administrator" not in user_roles and project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return project

@router.post("/{project_id}/optimize", response_model=OptimizationOut)
def run_optimization(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_role(["Planner", "GIS Analyst", "Project Manager"]))
):
    try:
        verify_project_access(project_id, db, current_user)
        res = optimize_project_deployment(project_id, db)
        return res
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Optimization error: {str(e)}")
