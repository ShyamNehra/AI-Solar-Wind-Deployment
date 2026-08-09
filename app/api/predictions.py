from fastapi import APIRouter, Depends, HTTPException, status
from schemas.prediction import PredictionRequest, ScorePredictionResponse, RecommendationPredictionResponse
from app.services.prediction_service import PredictionService

from app.data_sources.nasa_power import NASAPowerClient
from app.data_sources.global_wind_atlas import GlobalWindAtlasClient
from services.feature_engineering.solar import SolarFeatureEngineer
from services.feature_engineering.wind import WindFeatureEngineer

router = APIRouter(prefix="/predictions", tags=["Predictions"])

# Initialize the prediction service (loads models once at module import)
prediction_service = PredictionService()

def get_prediction_service() -> PredictionService:
    """
    Dependency injection provider for the PredictionService.
    """
    return prediction_service

def get_solar_engineer() -> SolarFeatureEngineer:
    """
    Dependency injection provider for the SolarFeatureEngineer.
    """
    return SolarFeatureEngineer(nasa_client=NASAPowerClient())

def get_wind_engineer() -> WindFeatureEngineer:
    """
    Dependency injection provider for the WindFeatureEngineer.
    """
    return WindFeatureEngineer(wind_client=GlobalWindAtlasClient())

def prepare_prediction_features(
    request: PredictionRequest,
    solar_engineer: SolarFeatureEngineer,
    wind_engineer: WindFeatureEngineer
) -> dict:
    """
    Helper function to resolve the required ML feature dictionary.
    Supports either coordinate-based lookup (via existing feature engineering modules)
    or direct feature overrides.
    """
    # 1. Coordinate-based lookup path (preferred if both latitude and longitude exist)
    if request.latitude is not None and request.longitude is not None:
        latitude = request.latitude
        longitude = request.longitude
        
        # Coordinate boundary validation
        if not (-90.0 <= latitude <= 90.0):
            raise ValueError("Latitude must be between -90.0 and 90.0 degrees.")
        if not (-180.0 <= longitude <= 180.0):
            raise ValueError("Longitude must be between -180.0 and 180.0 degrees.")

        # Extract features using existing pipeline modules
        solar_data = solar_engineer.get_solar_features(latitude, longitude)
        wind_data = wind_engineer.get_wind_features(latitude, longitude)
        
        return {
            "solar_irradiance": solar_data["solar_irradiance"],
            "wind_speed": wind_data["wind_speed"],
            "temperature": solar_data["temperature"],
            "humidity": solar_data["humidity"],
            "elevation": request.elevation,
            "slope": request.slope,
            "distance_to_road": request.distance_to_road,
            "distance_to_grid": request.distance_to_grid,
            "protected_area_distance": request.protected_area_distance,
            "environmental_impact_level": request.environmental_impact_level,
            "land_cost_per_acre": request.land_cost_per_acre,
            "grid_connection_cost": request.grid_connection_cost
        }
        
    # 2. Direct feature override path
    else:
        if (request.solar_irradiance is None or request.wind_speed is None or
            request.temperature is None or request.humidity is None):
            raise ValueError(
                "Incomplete features: Either provide both latitude and longitude, "
                "or provide all meteorological features (solar_irradiance, wind_speed, temperature, humidity)."
            )
            
        return {
            "solar_irradiance": request.solar_irradiance,
            "wind_speed": request.wind_speed,
            "temperature": request.temperature,
            "humidity": request.humidity,
            "elevation": request.elevation,
            "slope": request.slope,
            "distance_to_road": request.distance_to_road,
            "distance_to_grid": request.distance_to_grid,
            "protected_area_distance": request.protected_area_distance,
            "environmental_impact_level": request.environmental_impact_level,
            "land_cost_per_acre": request.land_cost_per_acre,
            "grid_connection_cost": request.grid_connection_cost
        }


@router.post(
    "/suitability",
    response_model=ScorePredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Predict site suitability score",
    description="Uses a trained ML Regressor to predict the overall suitability score of a site based on physical/meteorological features or coordinates, including explainability details."
)
def predict_suitability(
    request: PredictionRequest,
    service: PredictionService = Depends(get_prediction_service),
    solar_eng: SolarFeatureEngineer = Depends(get_solar_engineer),
    wind_eng: WindFeatureEngineer = Depends(get_wind_engineer)
):
    try:
        site_data = prepare_prediction_features(request, solar_eng, wind_eng)
        predicted_score = service.predict_suitability_score(site_data)
        
        # Explainability: Extract Top 3 features and construct explanation
        top_features = service.get_feature_importance_regressor()
        explanation = f"Prediction is primarily influenced by {top_features[0]['feature']} and {top_features[1]['feature']}."
        
        return ScorePredictionResponse(
            predicted_overall_score=predicted_score,
            top_features=top_features,
            explanation=explanation,
            status="Success"
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except (ConnectionError, TimeoutError) as ce:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Network error connecting to external feature sources: {str(ce)}"
        )
    except RuntimeError as re:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(re)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during suitability prediction: {str(e)}"
        )


@router.post(
    "/recommendation",
    response_model=RecommendationPredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Predict technology recommendation",
    description="Uses a trained ML Classifier to predict the deployment recommendation ('Solar', 'Wind', 'Hybrid', 'None') for a site based on features or coordinates, including explainability details."
)
def predict_recommendation(
    request: PredictionRequest,
    service: PredictionService = Depends(get_prediction_service),
    solar_eng: SolarFeatureEngineer = Depends(get_solar_engineer),
    wind_eng: WindFeatureEngineer = Depends(get_wind_engineer)
):
    try:
        site_data = prepare_prediction_features(request, solar_eng, wind_eng)
        predicted_rec = service.predict_deployment_recommendation(site_data)
        
        # Explainability: Extract Top 3 features and construct explanation
        top_features = service.get_feature_importance_classifier()
        explanation = f"Prediction is primarily influenced by {top_features[0]['feature']} and {top_features[1]['feature']}."
        
        return RecommendationPredictionResponse(
            predicted_deployment=predicted_rec,
            top_features=top_features,
            explanation=explanation,
            status="Success"
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except (ConnectionError, TimeoutError) as ce:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Network error connecting to external feature sources: {str(ce)}"
        )
    except RuntimeError as re:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(re)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during recommendation prediction: {str(e)}"
        )
