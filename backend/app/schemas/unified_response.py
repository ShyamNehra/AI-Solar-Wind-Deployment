"""
Unified Deployment Response Model

Standardized API response structure returned across all analysis & deployment endpoints.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any, Union


class ConstraintSummary(BaseModel):
    hard_constraints_passed: bool = Field(True, description="True if all mandatory hard constraints are satisfied")
    hard_constraint_violations: List[str] = Field(default_factory=list, description="List of violated hard constraints")
    soft_constraint_score: float = Field(86.0, description="Soft constraint feasibility score (0-100)")


class EnergyYieldMetrics(BaseModel):
    solar_annual_energy: float = Field(0.0, description="Annual Solar energy yield in kWh/year")
    wind_annual_energy: float = Field(0.0, description="Annual Wind energy yield in kWh/year")
    hybrid_annual_energy: float = Field(0.0, description="Annual Hybrid energy yield in kWh/year")
    selected_annual_energy_yield: float = Field(0.0, description="Selected annual energy yield for target deployment in kWh/year")


class FinancialMetrics(BaseModel):
    annual_revenue: float = Field(0.0, description="Estimated annual revenue")
    estimated_project_cost: float = Field(0.0, description="Estimated total project cost (CAPEX)")
    payback_period: float = Field(0.0, description="Estimated payback period in years")
    roi: float = Field(0.0, description="Return on Investment percentage (%)")


class UnifiedDeploymentResponse(BaseModel):
    model_config = ConfigDict(extra='allow')

    site_suitability: str = Field(..., description="Overall site suitability rating e.g. High, Moderate, Low, Poor, Not Suitable")
    recommended_deployment: str = Field(..., description="Recommended deployment strategy e.g. Recommended for Solar Deployment, Recommended for Wind Deployment, Recommended for Hybrid Deployment, Technically Not Feasible, Not Recommended")
    prediction: str = Field(..., description="Machine Learning predicted strategy")
    prediction_confidence: float = Field(85.0, description="Prediction confidence score percentage (0-100%)")

    technical_feasibility: bool = Field(..., description="True if technical feasibility validation passes hard constraints")
    feasibility_score: float = Field(..., description="Technical feasibility score (0-100)")

    constraint_summary: Union[ConstraintSummary, Dict[str, Any], List[str], str] = Field(..., description="Summary of hard/soft constraints")

    annual_energy_yield: float = Field(0.0, description="Estimated annual energy yield in kWh/year")

    annual_revenue: float = Field(0.0, description="Estimated annual revenue in currency")
    estimated_project_cost: float = Field(0.0, description="Estimated total project cost (CAPEX)")
    payback_period: float = Field(0.0, description="Estimated payback period in years")
    roi: float = Field(0.0, description="Return on Investment percentage (%)")

    feature_importance: Union[List[Dict[str, Any]], Dict[str, float]] = Field(default_factory=list, description="Feature importances")
    prediction_explanation: str = Field(..., description="Explainable AI explanation string")

    recommendation_reason: str = Field(..., description="Engineering recommendation rationale")

    status: str = Field("Success", description="Execution status")

    # Fields for backward compatibility
    solar_energy_yield: Optional[float] = Field(None, description="Annual Solar energy yield (kWh/year)")
    wind_energy_yield: Optional[float] = Field(None, description="Annual Wind energy yield (kWh/year)")
    hybrid_energy_yield: Optional[float] = Field(None, description="Annual Hybrid energy yield (kWh/year)")
    energy_yield: Optional[Union[EnergyYieldMetrics, Dict[str, Any]]] = Field(None, description="Energy yield metrics breakdown")
    financial_metrics: Optional[Union[FinancialMetrics, Dict[str, Any]]] = Field(None, description="Financial metrics breakdown")

    latitude: Optional[float] = Field(None, description="Site latitude")
    longitude: Optional[float] = Field(None, description="Site longitude")
    site_id: Optional[Union[int, str]] = Field(None, description="Site ID if registered")
    details: Optional[Dict[str, Any]] = Field(None, description="Extended pipeline details for backward compatibility")

    # ── Assessment sub-objects ─────────────────────────────────────────────────
    # These fields are populated by WorkflowPipelineService.run_pipeline() and
    # are required by the frontend Key Parameters cards, charts, and report
    # sections.  extra='allow' (above) ensures future pipeline additions also
    # pass through without schema changes.
    assessment_result: Optional[Dict[str, Any]] = Field(None, description="Full assessment result from AssessmentService")
    weather_summary: Optional[Dict[str, Any]] = Field(None, description="Weather data: solar_irradiance, temperature, humidity, rainfall, cloud_cover")
    solar_assessment: Optional[Dict[str, Any]] = Field(None, description="Solar assessment result")
    wind_assessment: Optional[Dict[str, Any]] = Field(None, description="Wind assessment result")
    terrain_assessment: Optional[Dict[str, Any]] = Field(None, description="Terrain assessment: elevation, slope, terrain_score")
    infrastructure_assessment: Optional[Dict[str, Any]] = Field(None, description="Infrastructure assessment: nearest_road, nearest_substation, accessibility_score")
    suitability_score: Optional[Dict[str, Any]] = Field(None, description="Suitability score breakdown")
    deployment_recommendation: Optional[Dict[str, Any]] = Field(None, description="Deployment recommendation from strategy engine")
    candidate_ranking: Optional[List[Dict[str, Any]]] = Field(None, description="Ranked candidate sites")
    deployment_optimization: Optional[Dict[str, Any]] = Field(None, description="Deployment optimization results")
    forecasting: Optional[Dict[str, Any]] = Field(None, description="Energy forecasting results")
    investment_recommendation: Optional[Dict[str, Any]] = Field(None, description="Investment recommendation metrics")
    energy_yield_estimation: Optional[Dict[str, Any]] = Field(None, description="Detailed energy yield estimation")
    financial_analysis: Optional[Dict[str, Any]] = Field(None, description="Detailed financial analysis")
    deployment: Optional[str] = Field(None, description="Raw deployment type (Solar / Wind / Hybrid)")
