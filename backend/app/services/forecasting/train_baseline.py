import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score

# Directory configuration for saved models
MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "models"))
MODEL_PATH = os.path.join(MODEL_DIR, "baseline_rf_model.joblib")


def generate_synthetic_data(n_samples: int = 1500) -> pd.DataFrame:
    """Generates dummy feature-engineered solar/wind dataset for baseline training."""
    np.random.seed(42)
    dates = pd.date_range(start="2023-01-01", periods=n_samples, freq="D")
    
    data = {
        "date": dates,
        "solar_irradiance": np.random.uniform(2.0, 7.5, n_samples),
        "wind_speed": np.random.uniform(1.0, 15.0, n_samples),
        "slope": np.random.uniform(0.0, 25.0, n_samples),
        "month": dates.month,
        "day_of_year": dates.dayofyear,
        "is_weekend": dates.dayofweek.isin([5, 6]).astype(int),
    }
    
    # Target: Generated Power Output (kWh/day) based on physical attributes + random noise
    df = pd.DataFrame(data)
    df["target_power_kwh"] = (
        (df["solar_irradiance"] * 45.0) 
        + (df["wind_speed"] ** 2 * 0.8) 
        - (df["slope"] * 1.2) 
        + np.random.normal(0, 10, n_samples)
    )
    return df


def task_1_prepare_dataset(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Task 1 — Prepare the Dataset Split (70% Train, 15% Val, 15% Test).
    Reasoning: Gives enough data for training (70%), an unbiased check for model tuning (15%), 
    and a final exam set (15%) to prevent data leakage.
    """
    print("\n[Task 1] Splitting dataset into Train (70%), Validation (15%), and Test (15%)...")
    
    feature_cols = [
        "solar_irradiance", "wind_speed", "slope",
        "month", "day_of_year", "is_weekend"
    ]
    target_col = "target_power_kwh"

    X = df[feature_cols]
    y = df[target_col]

    # Step 1: Split off 15% for final testing
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=0.15, random_state=42, shuffle=True
    )

    # Step 2: Split remaining 85% into Train (70% total) and Validation (15% total)
    # 0.1765 of 85% is approximately 15% of the overall dataset
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=0.1765, random_state=42, shuffle=True
    )

    print(f"  -> Train samples: {len(X_train)} | Val samples: {len(X_val)} | Test samples: {len(X_test)}")
    
    return {
        "X_train": X_train, "y_train": y_train,
        "X_val": X_val, "y_val": y_val,
        "X_test": X_test, "y_test": y_test,
        "features": feature_cols
    }


def task_2_train_models(data: Dict[str, Any]) -> Dict[str, Any]:
    """Task 2 — Train Two Baseline Models (Decision Tree vs. Random Forest)."""
    print("\n[Task 2] Training two baseline algorithms...")
    
    X_train, y_train = data["X_train"], data["y_train"]

    # Model 1: Decision Tree
    dt_model = DecisionTreeRegressor(random_state=42, max_depth=10)
    dt_model.fit(X_train, y_train)

    # Model 2: Random Forest
    rf_model = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)
    rf_model.fit(X_train, y_train)

    print("  -> Trained DecisionTreeRegressor and RandomForestRegressor successfully.")
    
    return {"dt": dt_model, "rf": rf_model}


def task_3_compare_models(models: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
    """Task 3 — Compare Model Performance on Validation Set."""
    print("\n[Task 3] Evaluating models on the Validation Set...")
    
    X_val, y_val = data["X_val"], data["y_val"]
    results = {}

    for name, model in models.items():
        val_preds = model.predict(X_val)
        mae = mean_absolute_error(y_val, val_preds)
        rmse = root_mean_squared_error(y_val, val_preds)
        r2 = r2_score(y_val, val_preds)
        
        results[name] = {
            "MAE": round(float(mae), 4),
            "RMSE": round(float(rmse), 4),
            "R2": round(float(r2), 4)
        }

    print("\n" + "="*45)
    print("      VALIDATION SET COMPARISON TABLE")
    print("="*45)
    print(f"{'Metric':<10} | {'Decision Tree':<15} | {'Random Forest':<15}")
    print("-" * 45)
    print(f"{'MAE':<10} | {results['dt']['MAE']:<15} | {results['rf']['MAE']:<15}")
    print(f"{'RMSE':<10} | {results['dt']['RMSE']:<15} | {results['rf']['RMSE']:<15}")
    print(f"{'R² Score':<10} | {results['dt']['R2']:<15} | {results['rf']['R2']:<15}")
    print("="*45 + "\n")

    return results


def task_4_analyze_behavior(models: Dict[str, Any], data: Dict[str, Any], val_results: Dict[str, Dict[str, float]]) -> None:
    """Task 4 — Analyze Model Behavior (Underfitting / Overfitting / Generalizing)."""
    print("[Task 4] Analyzing model behavior (Train vs. Validation performance)...")
    
    X_train, y_train = data["X_train"], data["y_train"]

    for name, model in models.items():
        train_preds = model.predict(X_train)
        train_mae = mean_absolute_error(y_train, train_preds)
        val_mae = val_results[name]["MAE"]

        print(f"\nModel: {name.upper()}")
        print(f"  - Training MAE:   {train_mae:.4f}")
        print(f"  - Validation MAE: {val_mae:.4f}")

        # Diagnosis logic
        if train_mae < (val_mae * 0.5):
            print("  - Diagnosis: OVERFITTING (Low train error, higher validation error).")
        elif train_mae > 20 and val_mae > 20:
            print("  - Diagnosis: UNDERFITTING (High error on both train and validation).")
        else:
            print("  - Diagnosis: GENERALIZING WELL (Train and Validation errors are balanced and low).")


def task_5_persist_best_model(models: Dict[str, Any], val_results: Dict[str, Dict[str, float]], filepath: str) -> None:
    """Task 5 — Save the Best-Performing Model to Disk."""
    # Choose best model based on lowest MAE on Validation set
    best_model_key = min(val_results, key=lambda k: val_results[k]["MAE"])
    best_model = models[best_model_key]

    print(f"\n[Task 5] Best model identified: {best_model_key.upper()}")
    print(f"Persisting model to disk: {filepath}")
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    joblib.dump(best_model, filepath)
    print("Model persisted successfully! Ready for FastAPI deployment.")


def run_pipeline():
    """Executes Tasks 1 through 5 sequentially."""
    print("=== STARTING BASELINE MACHINE LEARNING PIPELINE ===")
    
    dataset = generate_synthetic_data(n_samples=1500)
    
    data = task_1_prepare_dataset(dataset)
    models = task_2_train_models(data)
    val_results = task_3_compare_models(models, data)
    task_4_analyze_behavior(models, data, val_results)
    task_5_persist_best_model(models, val_results, MODEL_PATH)

    print("\n=== PIPELINE EXECUTION COMPLETE ===")


if __name__ == "__main__":
    run_pipeline()