from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.database.database import Base
from datetime import datetime, timezone

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    site_id = Column(Integer, ForeignKey("sites.id", ondelete="SET NULL"), nullable=True, index=True)
    
    report_type = Column(String(50), nullable=False)  # site_assessment, solar_potential, wind_potential, feasibility, investment
    file_format = Column(String(10), nullable=False)  # PDF, Excel
    file_path = Column(String(255), nullable=False)
    
    generated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
