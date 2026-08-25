import sys
import os

# Add root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from schemas.prediction import PredictionRequest
from app.services.prediction_service import PredictionService
from app.api.predictions import (
    predict_suitability,
    predict_recommendation,
    get_solar_engineer,
    get_wind_engineer
)

def test_prediction_explainability():
    print("=== Testing ML Prediction Explainability Output ===")
    service = PredictionService()
    solar_eng = get_solar_engineer()
    wind_eng = get_wind_engineer()
    
    # Odisha Coast coordinates
    request = PredictionRequest(
        latitude=19.8135,
        longitude=85.8312,
        elevation=25.0,
        slope=1.5
    )
    
    # 1. Suitability Prediction explainability
    suit_resp = predict_suitability(
        request, service=service, solar_eng=solar_eng, wind_eng=wind_eng
    )
    print(f"Suitability Score: {suit_resp.predicted_overall_score}")
    print(f"Top 3 Features: {suit_resp.top_features}")
    print(f"Explanation: {suit_resp.explanation}")
    
    assert len(suit_resp.top_features) == 3, f"Expected 3 top features, got {len(suit_resp.top_features)}"
    assert "primarily influenced by" in suit_resp.explanation
    
    # Check that they are sorted descending
    assert suit_resp.top_features[0].importance >= suit_resp.top_features[1].importance
    assert suit_resp.top_features[1].importance >= suit_resp.top_features[2].importance
    
    # 2. Recommendation Prediction explainability
    rec_resp = predict_recommendation(
        request, service=service, solar_eng=solar_eng, wind_eng=wind_eng
    )
    print(f"\nRecommendation: {rec_resp.predicted_deployment}")
    print(f"Top 3 Features: {rec_resp.top_features}")
    print(f"Explanation: {rec_resp.explanation}")
    
    assert len(rec_resp.top_features) == 3, f"Expected 3 top features, got {len(rec_resp.top_features)}"
    assert "primarily influenced by" in rec_resp.explanation
    assert rec_resp.top_features[0].importance >= rec_resp.top_features[1].importance
    
    print("[OK] Prediction explainability tests passed successfully!\n")

if __name__ == "__main__":
    test_prediction_explainability()
