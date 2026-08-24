import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    report_type = Column(String, nullable=False) # PDF, CSV, Feasibility
    file_path = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="reports")
    """
    Report model — links a generated assessment report to a Site and its owning User.
    Satisfies the DB relationships requirement for Milestone 1.
    """
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    report_type = Column(String, nullable=False, default="Assessment")
    summary = Column(Text, nullable=True)
    deployment_recommendation = Column(String, nullable=True)
    overall_suitability_score = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # FK → Site
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=True)
    # FK → User (report creator)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    site = relationship("Site", back_populates="reports")
    created_by = relationship("User", back_populates="reports")
