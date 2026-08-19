import os
import sys
from pathlib import Path

# Ensure the backend directory is in the Python path
BACKEND_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND_DIR))

try:
    from app.services.forecasting.forecast_service import ForecastingService
except ImportError as e:
    print(f"[ERROR] Import failed. Ensure you run this script from the 'backend' directory: {e}")
    sys.exit(1)


def verify_forecasting_ensemble():
    print("==================================================================")
    print("      VERIFYING FORECASTING SERVICE & 60/40 HYBRID ENSEMBLE      ")
    print("==================================================================")

    # 1. Initialize ForecastingService
    service = ForecastingService()

    # Verify which models were loaded
    print("\n--- MODEL LOADING STATUS ---")
    print(f"Active Architecture : {service.model_name}")
    print(f"XGBoost Loaded     : {service._xgb_model is not None}")
    print(f"Random Forest Loaded: {service._rf_model is not None}")

    if service._xgb_model is None or service._rf_model is None:
        print("\n[WARNING] One or both ML model binaries were not found.")
        print("  * Run `python scripts/train_candidate_model.py` to generate model binaries in the models/ directory.")

    # 2. Prepare Sample Test Payloads
    sample_env_features = {
        "latitude": 27.5397,
        "longitude": 71.9152,
        "solar_irradiance": 6.2,
        "wind_speed": 4.8,
        "slope": 2.1,
        "elevation": 169.0,
        "land_use_type": "clear"
    }

    print("\n--- RUNNING HYBRID ENSEMBLE FORECAST ---")
    print(f"Input Location : Bhadla Solar Desert ({sample_env_features['latitude']}, {sample_env_features['longitude']})")
    print(f"Resource Inputs: Solar GHI = {sample_env_features['solar_irradiance']} kWh/m²/day | Wind Speed = {sample_env_features['wind_speed']} m/s")

    # 3. Execute Pipeline
    try:
        results = service.run_forecast(
            deployment_type="Solar",
            time_series_df=None,
            env_features=sample_env_features
        )

        # 4. Display Outputs
        print("\n--- PIPELINE ASSESSMENT RESULTS ---")
        print(f"Status               : {results['status']}")
        print(f"Recommended Type     : {results['recommended_deployment']}")
        print(f"Effective Type       : {results['deployment_type']}")
        print(f"Overall Suitability  : {results['site_suitability']['overall_score']} / 100")
        
        print("\n--- ML ENSEMBLE PREDICTION OUTPUT ---")
        print(f"Predicted Power (kW) : {results['ml_prediction']['predicted_power_kw']} kW")
        print(f"Records Evaluated    : {results['ml_prediction']['records_evaluated']}")
        print(f"Driver Explanation   : {results['ml_prediction']['explanation']['summary_text']}")

        print("\n--- MODEL METADATA ---")
        metadata = results["model_behavior"]
        print(f"Model Architecture   : {metadata['selected_model']['architecture']}")
        print(f"R² Score Metric      : {metadata['evaluation_metrics']['r2_score']}")
        print(f"MAE Metric           : {metadata['evaluation_metrics']['mae_mwh']} MWh")

        print("\n==================================================================")
        print("  [SUCCESS] ForecastingService Ensemble Execution Verified!       ")
        print("==================================================================")

    except Exception as e:
        print(f"\n[ERROR] Pipeline execution failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    verify_forecasting_ensemble()