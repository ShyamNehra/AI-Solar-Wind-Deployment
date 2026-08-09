from pydantic import BaseModel, Field
from schemas.prediction import FeatureImportanceItem

class AnalysisRequest(BaseModel):
    project_name: str = Field(..., description="Name of the renewable energy project")
    location: str = Field(..., description="Geographical location name")
    latitude: float = Field(..., description="Latitude coordinate between -90.0 and 90.0")
    longitude: float = Field(..., description="Longitude coordinate between -180.0 and 180.0")
    
    # Optional parameters for site suitability evaluation with defaults matching the scoring engine
    elevation: float = Field(0.0, description="Elevation in meters")
    slope: float = Field(0.0, description="Slope in degrees")
    distance_to_road: float = Field(0.0, description="Distance to nearest road in km")
    distance_to_grid: float = Field(0.0, description="Distance to nearest transmission grid in km")
    protected_area_distance: float = Field(10.0, description="Distance to protected areas in km")
    environmental_impact_level: float = Field(0.0, description="Environmental impact level (0.0 to 10.0)")
    land_cost_per_acre: float = Field(10000.0, description="Land cost per acre in USD")
    grid_connection_cost: float = Field(50000.0, description="Grid connection cost in USD")

    # Optional parameters for annual energy yield estimation
    installed_capacity_kw: float = Field(1000.0, description="Installed system capacity in kW (default 1MW = 1000kW)")
    solar_system_efficiency: float = Field(0.80, description="Overall system efficiency for solar (default 80%)")
    wind_operational_losses: float = Field(0.15, description="Overall operational losses for wind (default 15%)")
    solar_capacity_factor: float | None = Field(None, description="Optional custom solar capacity factor override (0.0 to 1.0)")
    wind_capacity_factor: float | None = Field(None, description="Optional custom wind capacity factor override (0.0 to 1.0)")


class ProjectInfo(BaseModel):
    project_name: str
    location: str
    latitude: float
    longitude: float


class SolarFeatures(BaseModel):
    solar_irradiance: float
    temperature: float
    humidity: float


class WindFeatures(BaseModel):
    wind_speed: float
    wind_direction: float
    wind_power_density: float


class SiteEvaluation(BaseModel):
    resource_score: float
    terrain_score: float
    infrastructure_score: float
    environmental_score: float
    economic_score: float


class SiteScore(BaseModel):
    overall_score: float


class DeploymentRecommendation(BaseModel):
    deployment: str
    confidence: int
    reason: str


class AnalysisResponse(BaseModel):
    project: ProjectInfo
    solar_features: SolarFeatures
    wind_features: WindFeatures
    site_evaluation: SiteEvaluation
    site_score: SiteScore
    deployment_recommendation: DeploymentRecommendation

    # ML Predictions (Explainability)
    predicted_overall_score: float | None = Field(None, description="ML predicted overall site suitability score")
    predicted_deployment: str | None = Field(None, description="ML predicted technology deployment recommendation")
    top_features: list[FeatureImportanceItem] | None = Field(None, description="Top 3 most influential ML features")
    explanation: str | None = Field(None, description="Explainability explanation text")

    # Technical Feasibility
    technical_feasibility: bool = Field(..., description="Whether the site is technically feasible (fails no hard constraints)")
    technical_feasibility_score: int = Field(..., description="Calculated feasibility score from soft constraints")
    constraint_violations: int = Field(..., description="Number of critical constraint violations")
    critical_violations: list[str] = Field(..., description="List of violated critical engineering constraints")
    overall_status: str = Field(..., description="Overall engineering status ('Feasible' or 'Unfeasible')")

    # Energy Yield Estimation
    solar_energy_yield_kwh: float = Field(..., description="Estimated annual solar energy generation in kWh")
    wind_energy_yield_kwh: float = Field(..., description="Estimated annual wind energy generation in kWh")
    hybrid_energy_yield_kwh: float = Field(..., description="Estimated annual hybrid energy generation in kWh")
    recommended_annual_energy_kwh: float = Field(..., description="Estimated annual energy generation for the recommended technology in kWh")
