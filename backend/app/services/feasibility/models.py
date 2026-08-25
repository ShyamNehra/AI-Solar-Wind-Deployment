"""
Data and Pydantic models for Technical Feasibility Validation Engine.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class HardConstraintResult(BaseModel):
    passed: bool = Field(..., description="True if all mandatory hard constraints are satisfied")
    violations: List[str] = Field(default_factory=list, description="List of exact failed hard constraint descriptions")


class SoftConstraintResult(BaseModel):
    road_distance: float = Field(default=80.0, ge=0.0, le=100.0)
    grid_access: float = Field(default=80.0, ge=0.0, le=100.0)
    accessibility: float = Field(default=80.0, ge=0.0, le=100.0)
    terrain: float = Field(default=80.0, ge=0.0, le=100.0)
    infrastructure: float = Field(default=80.0, ge=0.0, le=100.0)
    environmental_risk: float = Field(default=80.0, ge=0.0, le=100.0)


class FeasibilityResult(BaseModel):
    technical_feasibility: bool = Field(..., description="Overall feasibility boolean (False if any hard constraint fails)")
    feasibility_score: float = Field(..., ge=0.0, le=100.0, description="Overall weighted feasibility score (0-100)")
    feasibility_rating: str = Field(..., description="'Excellent' | 'Good' | 'Moderate' | 'Poor'")
    engineering_decision: str = Field(..., description="'Approved' | 'Feasible for Deployment' | 'NOT FEASIBLE'")
    engineering_recommendation: str = Field(..., description="Concise engineering rationale and summary")
    hard_constraints: HardConstraintResult
    soft_constraints: Dict[str, float]
    constraint_summary: List[str] = Field(default_factory=list)
