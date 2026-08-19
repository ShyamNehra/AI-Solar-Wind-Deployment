from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.db.postgres import get_db
from app.models.user import User
from app.models.site import Site
from app.api.dependencies import require_any_role
from app.services.report_generator import generate_pdf_report, generate_excel_report

router = APIRouter(prefix="/sites", tags=["Reports"])

def verify_site_access(site_id: int, db: Session, current_user: User) -> Site:
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")
        
    project = site.project
    user_roles = [role.name for role in current_user.roles]
    if "Administrator" not in user_roles and project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return site

@router.post("/{site_id}/reports/export")
def export_report(
    site_id: int,
    format: str = Query(..., pattern="^(pdf|excel)$"),
    report_type: str = Query("site_assessment", pattern="^(site_assessment|potential|feasibility)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_role(["Planner", "GIS Analyst", "Project Manager"]))
):
    verify_site_access(site_id, db, current_user)
    try:
        if format == "pdf":
            file_data = generate_pdf_report(site_id, report_type, db)
            media_type = "application/pdf"
            filename = f"site_{site_id}_{report_type}_report.pdf"
        else:
            file_data = generate_excel_report(site_id, report_type, db)
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = f"site_{site_id}_{report_type}_report.xlsx"
            
        headers = {
            "Content-Disposition": f"attachment; filename={filename}"
        }
        return Response(content=file_data, media_type=media_type, headers=headers)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Export error: {str(e)}")
