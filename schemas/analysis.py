from pydantic import BaseModel, Field

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
