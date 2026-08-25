from pydantic import BaseModel, Field

class PredictionRequest(BaseModel):
    latitude: float | None = Field(None, description="Latitude coordinate between -90.0 and 90.0")
    longitude: float | None = Field(None, description="Longitude coordinate between -180.0 and 180.0")

    solar_irradiance: float | None = Field(None, description="Solar irradiance in kWh/m²/day")
    wind_speed: float | None = Field(None, description="Wind speed in m/s")
    temperature: float | None = Field(None, description="Average temperature in °C")
    humidity: float | None = Field(None, description="Relative humidity percentage")
    
    elevation: float = Field(0.0, description="Elevation in meters")
    slope: float = Field(0.0, description="Slope in degrees")
    distance_to_road: float = Field(0.0, description="Distance to nearest road in km")
    distance_to_grid: float = Field(0.0, description="Distance to nearest transmission grid in km")
    protected_area_distance: float = Field(10.0, description="Distance to protected areas in km")
    environmental_impact_level: float = Field(0.0, description="Environmental impact level (0.0 to 10.0)")
    land_cost_per_acre: float = Field(10000.0, description="Land cost per acre in USD")
    grid_connection_cost: float = Field(50000.0, description="Grid connection cost in USD")


class FeatureImportanceItem(BaseModel):
    feature: str = Field(..., description="Name of the input feature")
    importance: float = Field(..., description="Calculated feature importance weight between 0.0 and 1.0")


class ScorePredictionResponse(BaseModel):
    predicted_overall_score: float = Field(..., description="ML predicted overall site suitability score")
    top_features: list[FeatureImportanceItem] = Field(..., description="Top 3 most influential features in descending order")
    explanation: str = Field(..., description="Natural language explanation of the key influences")
    status: str = Field("Success", description="Status message")


class RecommendationPredictionResponse(BaseModel):
    predicted_deployment: str = Field(..., description="ML predicted technology deployment recommendation")
    top_features: list[FeatureImportanceItem] = Field(..., description="Top 3 most influential features in descending order")
    explanation: str = Field(..., description="Natural language explanation of the key influences")
    status: str = Field("Success", description="Status message")
