# scripts/explain_model.py
import os
import joblib
import pandas as pd

MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app", "models", "baseline_rf_model.joblib"))

FEATURE_NAMES = [
    "solar_irradiance",
    "wind_speed",
    "slope",
    "month",
    "day_of_year",
    "is_weekend"
]

def analyze_feature_importance():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")

    model = joblib.load(MODEL_PATH)
    
    #Extract feature importances
    importances = model.feature_importances_
    
    # Format and sort descending
    importance_df = pd.DataFrame({
        "Feature": FEATURE_NAMES,
        "Importance": importances
    }).sort_values(by="Importance", ascending=False).reset_index(drop=True)

    print("Feature Importances (Descending)")
    print(importance_df.to_string(index=False))

    #Domain Validation Logic
    top_features = importance_df["Feature"].iloc[:2].tolist()
    
    print("\n=== Task 2: Domain Validation ===")
    if "solar_irradiance" in top_features or "wind_speed" in top_features:
        print("✔ Validation Passed: Primary physical resource drivers (solar_irradiance / wind_speed) dominate energy yield predictions.")
    else:
        print("⚠ Validation Warning: Secondary/temporal features are unexpectedly ranking higher than primary energy sources.")

    return importance_df

if __name__ == "__main__":
    analyze_feature_importance()