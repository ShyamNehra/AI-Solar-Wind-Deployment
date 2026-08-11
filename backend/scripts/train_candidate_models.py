import os
import joblib
import numpy as np
import pandas as pd

from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split

# Import our custom ModelEvaluator from the app package
from app.evaluation.model_evaluator import ModelEvaluator

# Output path for saving model artifacts
MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app", "models"))
os.makedirs(MODEL_DIR, exist_ok=True)


def generate_synthetic_data(n_samples: int = 1000):
    """Generates synthetic solar/wind feature dataset for training candidate models."""
    np.random.seed(42)
    
    solar_irradiance = np.random.uniform(2.0, 8.0, n_samples)
    wind_speed = np.random.uniform(1.0, 15.0, n_samples)
    slope = np.random.uniform(0.0, 15.0, n_samples)
    month = np.random.randint(1, 13, n_samples)
    day_of_year = np.random.randint(1, 366, n_samples)
    is_weekend = np.random.choice([0, 1], n_samples)

    # Nonlinear target variable generation (Energy Yield in MWh)
    energy_yield = (
        (solar_irradiance * 25.0) +
        (wind_speed ** 1.8 * 1.5) -
        (slope * 0.8) +
        (np.sin(month / 12 * 2 * np.pi) * 10) +
        np.random.normal(0, 5.0, n_samples)
    )

    df = pd.DataFrame({
        "solar_irradiance": solar_irradiance,
        "wind_speed": wind_speed,
        "slope": slope,
        "month": month,
        "day_of_year": day_of_year,
        "is_weekend": is_weekend,
        "energy_yield": energy_yield
    })
    return df


def train_and_compare_models():
    print("Generating training dataset...")
    df = generate_synthetic_data(n_samples=1200)

    X = df[["solar_irradiance", "wind_speed", "slope", "month", "day_of_year", "is_weekend"]]
    y = df["energy_yield"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 1. Define candidate models
    candidate_models = {
        "Decision Tree": DecisionTreeRegressor(max_depth=8, random_state=42),
        "Random Forest": RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
    }

    evaluator = ModelEvaluator()
    evaluation_results = []
    trained_objects = {}

    print("\nTraining candidate models...")
    for name, model in candidate_models.items():
        # Fit model on training split
        model.fit(X_train, y_train)
        
        # Perform predictions on hold-out test set
        predictions = model.predict(X_test)
        
        # Calculate metrics using ModelEvaluator
        metrics = evaluator.calculate_regression_metrics(
            y_true=y_test.values, 
            y_pred=predictions, 
            model_name=name
        )
        evaluation_results.append(metrics)
        trained_objects[name] = model

    # Display evaluation summary
    comparison_df = evaluator.generate_comparison_table(evaluation_results)
    print("\nCandidate Model Performance Comparison:")
    print(comparison_df.to_string(index=False))

    # Save candidate artifacts for testing
    for name, model in trained_objects.items():
        filename = f"{name.lower().replace(' ', '_')}_model.joblib"
        path = os.path.join(MODEL_DIR, filename)
        joblib.dump(model, path)
        print(f"Saved {name} model artifact to: {path}")

if __name__ == "__main__":
    train_and_compare_models()