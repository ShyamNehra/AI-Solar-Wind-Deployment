import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, root_mean_squared_error
from xgboost import XGBRegressor

def explain_model(model, feature_names):
    """Prints feature importances for model interpretability."""
    print("\n--- FEATURE IMPORTANCE BREAKDOWN ---")
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
        for name, imp in sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True):
            print(f"  * {name.ljust(20)}: {imp*100:.2f}% contribution")

def train_candidate_models():
    print("==================================================")
    print("   TRAINING RANDOM FOREST & XGBOOST MODELS        ")
    print("==================================================")

    # 1. Dataset Path Resolution
    data_path = os.path.join(os.path.dirname(__file__), "../data/renewable_dataset.csv")
    models_dir = os.path.join(os.path.dirname(__file__), "../../models")
    os.makedirs(models_dir, exist_ok=True)

    # Load dataset or create synthetic baseline if missing
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
    else:
        print("[WARNING] Dataset CSV not found. Generating synthetic baseline data for training verification...")
        np.random.seed(42)
        n_samples = 1000
        df = pd.DataFrame({
            "latitude": np.random.uniform(8.0, 35.0, n_samples),
            "longitude": np.random.uniform(68.0, 96.0, n_samples),
            "solar_irradiance": np.random.uniform(3.0, 6.5, n_samples),
            "wind_speed": np.random.uniform(2.0, 9.0, n_samples),
            "slope": np.random.uniform(0.0, 20.0, n_samples),
            "elevation": np.random.uniform(0.0, 2000.0, n_samples),
        })
        # Realistic Target Formula: Solar + Wind driver minus Slope degradation
        df["expected_capacity_factor"] = (
            df["solar_irradiance"] * 4.2 + df["wind_speed"] * 2.8 - df["slope"] * 0.8 + np.random.normal(0, 1, n_samples)
        )

    feature_cols = ["latitude", "longitude", "solar_irradiance", "wind_speed", "slope", "elevation"]
    target_col = "expected_capacity_factor"

    X = df[feature_cols]
    y = df[target_col]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 2. Train Baseline Random Forest
    print("\n[1/2] Training Random Forest Regressor...")
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)
    rf_pred = rf_model.predict(X_test)

    rf_r2 = r2_score(y_test, rf_pred)
    print(f"  * RF R² Score : {rf_r2:.4f} | MAE: {mean_absolute_error(y_test, rf_pred):.4f}")
    explain_model(rf_model, feature_cols)

    # Save RF Model
    rf_path = os.path.join(models_dir, "baseline_rf_model.joblib")
    joblib.dump(rf_model, rf_path)
    print(f"  [SUCCESS] Random Forest saved to: {rf_path}")

    # 3. Train Candidate XGBoost Model
    print("\n[2/2] Training XGBoost Regressor (Mentor Recommendation)...")
    xgb_model = XGBRegressor(n_estimators=150, learning_rate=0.05, max_depth=5, random_state=42)
    xgb_model.fit(X_train, y_train)
    xgb_pred = xgb_model.predict(X_test)

    xgb_r2 = r2_score(y_test, xgb_pred)
    print(f"  * XGBoost R² Score : {xgb_r2:.4f} | MAE: {mean_absolute_error(y_test, xgb_pred):.4f}")
    explain_model(xgb_model, feature_cols)

    # Save XGBoost Model
    xgb_path = os.path.join(models_dir, "candidate_xgb_model.joblib")
    joblib.dump(xgb_model, xgb_path)
    print(f"  [SUCCESS] XGBoost saved to: {xgb_path}")

    print("\n==================================================")
    print(f" TRAINING COMPLETE | Selected Best Model: {'XGBoost' if xgb_r2 >= rf_r2 else 'Random Forest'}")
    print("==================================================")

if __name__ == "__main__":
    train_candidate_models()