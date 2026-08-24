"""
Pydantic Schemas for Machine Learning Baseline & FastAPI Endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union

class FeatureVector(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude")
    solar_irradiance: Optional[float] = Field(default=5.2, description="Solar Irradiance (kWh/m²/day)")
    wind_speed: Optional[float] = Field(default=6.8, description="Wind Speed (m/s)")
    temperature: Optional[float] = Field(default=24.5, description="Temperature (°C)")
    humidity: Optional[float] = Field(default=55.0, description="Relative Humidity (%)")
    elevation: Optional[float] = Field(default=250.0, description="Elevation (m)")
    slope: Optional[float] = Field(default=2.5, description="Terrain Slope (degrees)")
    road_distance: Optional[float] = Field(default=3.2, description="Distance to nearest road (km)")
    substation_distance: Optional[float] = Field(default=8.5, description="Distance to nearest substation (km)")
    accessibility: Optional[float] = Field(default=82.0, description="Accessibility score (0-100)")
    capacity_factor: Optional[float] = Field(default=28.5, description="Capacity factor (%)")
    environmental_score: Optional[float] = Field(default=85.0, description="Environmental score (0-100)")
    infrastructure_score: Optional[float] = Field(default=78.0, description="Infrastructure score (0-100)")
    terrain_score: Optional[float] = Field(default=80.0, description="Terrain score (0-100)")
    season: Optional[str] = Field(default="Summer", description="Season name")
    month: Optional[int] = Field(default=7, ge=1, le=12, description="Month (1-12)")
    day: Optional[int] = Field(default=15, ge=1, le=31, description="Day of month")
    week_number: Optional[int] = Field(default=28, ge=1, le=53, description="Week number")
    day_of_year: Optional[int] = Field(default=196, ge=1, le=366, description="Day of year")
    quarter: Optional[int] = Field(default=3, ge=1, le=4, description="Quarter (1-4)")
    weekend_flag: Optional[int] = Field(default=0, ge=0, le=1, description="1 if weekend else 0")
    leap_year_flag: Optional[int] = Field(default=0, ge=0, le=1, description="1 if leap year else 0")
    wind_class: Optional[str] = Field(default="Good", description="Wind Class category")
    solar_class: Optional[str] = Field(default="High", description="Solar Class category")
    protected_forest: Optional[bool] = Field(default=False, description="True if inside protected forest area")
    restricted_land_use: Optional[bool] = Field(default=False, description="True if land use is restricted")
    water_body: Optional[bool] = Field(default=False, description="True if site contains water body")
    national_park: Optional[bool] = Field(default=False, description="True if inside national park area")
    military_zone: Optional[bool] = Field(default=False, description="True if inside military restricted zone")
    airport_restricted_area: Optional[bool] = Field(default=False, description="True if inside airport restricted zone")
    flood_zone: Optional[bool] = Field(default=False, description="True if inside flood zone hazard")
    unsafe_terrain: Optional[bool] = Field(default=False, description="True if terrain is geologically unsafe")
    severe_environmental_restrictions: Optional[bool] = Field(default=False, description="True if severe environmental restrictions exist")

class TrainRequest(BaseModel):
    target_variable: Optional[str] = Field(default="solar_irradiance", description="Target variable to predict")
    model_type: Optional[str] = Field(default="auto", description="'regression' | 'classification' | 'auto'")
    algorithm: Optional[str] = Field(default="random_forest", description="'linear_regression' | 'decision_tree' | 'random_forest'")
    test_size: Optional[float] = Field(default=0.2, ge=0.05, le=0.5, description="Train-test split ratio")
    random_state: Optional[int] = Field(default=42, description="Random seed")
    hyperparameters: Optional[Dict[str, Any]] = Field(default=None, description="Model hyperparameters e.g. max_depth, n_estimators")

class CompareRequest(BaseModel):
    target_variable: Optional[str] = Field(default="solar_irradiance", description="Target variable to predict")
    model_type: Optional[str] = Field(default="auto", description="'regression' | 'classification' | 'auto'")
    algorithms: Optional[List[str]] = Field(default_factory=lambda: ["linear_regression", "decision_tree", "random_forest"], description="Algorithms to compare")
    random_state: Optional[int] = Field(default=42, description="Random seed")

class TrainResponse(BaseModel):
    status: str
    message: str
    training_completed: Optional[str] = None
    number_of_models_trained: Optional[int] = None
    best_model_selected: Optional[str] = None
    training_duration: Optional[float] = None
    algorithm: Optional[str] = None
    target_variable: Optional[str] = None
    prediction_type: Optional[str] = None
    saved_model_path: Optional[str] = None
    sample_count: Optional[int] = None
    metrics: Optional[Dict[str, Any]] = None
    model_behavior: Optional[str] = None
    top_feature_importances: Optional[Dict[str, float]] = None

class CompareResponse(BaseModel):
    status: str
    target_variable: str
    prediction_type: str
    split_info: Dict[str, Any]
    best_algorithm: str
    best_score: float
    best_model_selected: Optional[str] = None
    ranking_score: Optional[float] = None
    selection_reason: Optional[str] = None
    comparison_table: List[Dict[str, Any]]
    saved_model_path: str

class PredictRequest(BaseModel):
    feature_vector: Optional[FeatureVector] = Field(default=None, description="Specific feature values to predict for")
    latitude: Optional[float] = Field(default=None, ge=-90.0, le=90.0, description="Latitude for ad-hoc lookup")
    longitude: Optional[float] = Field(default=None, ge=-180.0, le=180.0, description="Longitude for ad-hoc lookup")
    model_type: Optional[str] = Field(default="regression", description="'regression' | 'classification'")

class PredictResponse(BaseModel):
    site_suitability: Optional[str] = "High Suitability"
    recommended_deployment: Optional[str] = "Hybrid Farm"
    prediction: Union[float, str, int]
    prediction_confidence: Optional[float] = 92.5
    confidence_score: float
    target_variable: str
    prediction_type: str
    feature_importance: Dict[str, float]
    prediction_status: str
    explanation: Optional[str] = None
    prediction_explanation: Optional[str] = None
    recommendation_reason: Optional[str] = None
    processing_time: Optional[float] = None
    processing_time_ms: Optional[float] = None
    selected_model: Optional[str] = None
    deployment: Optional[str] = None
    technical_feasibility: Optional[bool] = None
    feasibility_score: Optional[float] = None
    feasibility_rating: Optional[str] = None
    engineering_decision: Optional[str] = None
    engineering_recommendation: Optional[str] = None
    hard_constraints: Optional[Dict[str, Any]] = None
    soft_constraints: Optional[Dict[str, Any]] = None
    constraint_summary: Optional[Union[str, List[str], Dict[str, Any]]] = None
    annual_energy_yield: Optional[float] = None
    solar_energy_yield: Optional[float] = None
    wind_energy_yield: Optional[float] = None
    hybrid_energy_yield: Optional[float] = None
    annual_revenue: Optional[float] = None
    estimated_project_cost: Optional[float] = None
    payback_period: Optional[float] = None
    roi: Optional[float] = None
    status: Optional[str] = "Success"




class ModelStatusResponse(BaseModel):
    model_loaded: Optional[bool] = None
    model_name: Optional[str] = None
    training_date: Optional[str] = None
    dataset_rows: Optional[int] = None
    features: Optional[Union[List[str], int]] = None
    target_column: Optional[str] = None
    model_version: Optional[str] = None
    regressor_exists: bool
    classifier_exists: bool
    active_model_type: str
    target_variable: str
    algorithm: str
    sample_count: int
    metrics: Dict[str, Any]

class MetricsResponse(BaseModel):
    all_evaluation_metrics: Optional[Dict[str, Any]] = None
    comparison_table: Optional[List[Dict[str, Any]]] = None
    best_model_summary: Optional[Dict[str, Any]] = None
    regression_metrics: Optional[Dict[str, Any]] = None
    classification_metrics: Optional[Dict[str, Any]] = None
    overall_status: str


