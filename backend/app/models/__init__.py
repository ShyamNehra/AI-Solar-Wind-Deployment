from app.models.user import User, UserRole
from app.models.project import Project
from app.models.site import Site
from app.models.environmental_data import EnvironmentalData
from app.models.solar_prediction import SolarPrediction
from app.models.wind_prediction import WindPrediction
from app.models.suitability_score import SuitabilityScore
from app.models.report import Report

__all__ = [
    "User",
    "UserRole",
    "Project",
    "Site",
    "EnvironmentalData",
    "SolarPrediction",
    "WindPrediction",
    "SuitabilityScore",
    "Report",
]
"""
Models Package Initialization
Imports all SQLAlchemy ORM models to ensure full registry configuration across relationships.
"""

from app.models.user import User
from app.models.project import Project
from app.models.site import Site
from app.models.feature import Feature
from app.models.assessment import Assessment
from app.models.report import Report
from app.models.environmental_data import EnvironmentalData
from app.models.solar_prediction import SolarPrediction
from app.models.wind_prediction import WindPrediction
from app.models.feature_store import FeatureStore

__all__ = [
    "User",
    "Project",
    "Site",
    "Feature",
    "Assessment",
    "Report",
    "EnvironmentalData",
    "SolarPrediction",
    "WindPrediction",
    "FeatureStore",
]
