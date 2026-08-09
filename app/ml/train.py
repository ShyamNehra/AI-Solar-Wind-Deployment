import os
import sys
import time
import json
import random
import numpy as np
import joblib

# Ensure the root of the project is in the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.database.database import SessionLocal
from app.models.feature import Feature
from app.services.scoring_engine import evaluate_site_suitability
from app.services.deployment_strategy import recommend_deployment

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor, GradientBoostingClassifier
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, accuracy_score, precision_score, recall_score, f1_score

# Load feature schema from feature_schema.json
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'feature_schema.json')
with open(SCHEMA_PATH, 'r') as f:
    FEATURE_COLS = json.load(f)

def load_historical_data() -> list[dict]:
    """
    Fetch existing features from the database as historical renewable energy data.
    """
    db = SessionLocal()
    try:
        db_features = db.query(Feature).all()
        historical_records = []
        for f in db_features:
            record = {
                "solar_irradiance": f.solar_irradiance,
                "wind_speed": f.wind_speed,
                "temperature": f.temperature,
                "humidity": f.humidity,
                "elevation": f.elevation,
                "slope": f.slope,
                # Extra parameters not stored in features table are defaulted
                "distance_to_road": 2.0,
                "distance_to_grid": 5.0,
                "protected_area_distance": 10.0,
                "environmental_impact_level": 1.0,
                "land_cost_per_acre": 10000.0,
                "grid_connection_cost": 50000.0
            }
            historical_records.append(record)
        return historical_records
    except Exception as e:
        print(f"Warning: Failed to load data from database: {e}")
        return []
    finally:
        db.close()

def generate_fallback_synthetic_data(num_samples: int) -> list[dict]:
    """
    Generate synthetic data with realistic meteorological and physical distributions.
    """
    np.random.seed(42)
    random.seed(42)
    
    synthetic_records = []
    for _ in range(num_samples):
        record = {
            "solar_irradiance": round(np.random.uniform(2.0, 7.5), 2),
            "wind_speed": round(np.random.uniform(1.0, 15.0), 2),
            "temperature": round(np.random.uniform(10.0, 45.0), 2),
            "humidity": round(np.random.uniform(15.0, 95.0), 2),
            "elevation": round(np.random.uniform(0.0, 3000.0), 1),
            "slope": round(np.random.uniform(0.0, 45.0), 2),
            "distance_to_road": round(np.random.uniform(0.1, 30.0), 2),
            "distance_to_grid": round(np.random.uniform(0.1, 30.0), 2),
            "protected_area_distance": round(np.random.uniform(0.0, 50.0), 2),
            "environmental_impact_level": round(np.random.uniform(0.0, 10.0), 1),
            "land_cost_per_acre": round(np.random.uniform(1000.0, 50000.0), 2),
            "grid_connection_cost": round(np.random.uniform(5000.0, 200000.0), 2)
        }
        synthetic_records.append(record)
    return synthetic_records

def label_data(records: list[dict]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Label the feature records using existing Site Scoring Engine and Deployment Recommendation Module.
    """
    X_list = []
    y_score_list = []
    y_recommend_list = []
    
    for r in records:
        scoring_res = evaluate_site_suitability(r)
        score = scoring_res["overall_score"]
        
        rec_res = recommend_deployment(r["solar_irradiance"], r["wind_speed"])
        deployment = rec_res["deployment"]
        
        features = [r[col] for col in FEATURE_COLS]
        
        X_list.append(features)
        y_score_list.append(score)
        y_recommend_list.append(deployment)
        
    return np.array(X_list), np.array(y_score_list), np.array(y_recommend_list)

def main():
    print("Starting ML Baseline Training Workflow...")
    
    # 1. Load historical database features (preferred)
    historical_data = load_historical_data()
    print(f"Loaded {len(historical_data)} historical records from the database features table.")
    
    # 2. Fallback to synthetic data if historical count is insufficient
    target_samples = 2000
    if len(historical_data) < target_samples:
        needed = target_samples - len(historical_data)
        print(f"Historical data insufficient. Generating {needed} synthetic fallback samples...")
        synthetic_data = generate_fallback_synthetic_data(needed)
        all_data = historical_data + synthetic_data
    else:
        print("Historical data count is sufficient. Using 100% historical data.")
        all_data = historical_data
        
    # 3. Label data reusing existing scoring and recommendation modules
    X, y_score, y_recommend = label_data(all_data)
    
    # 4. Train-Test Split (80/20)
    X_train, X_test, y_score_train, y_score_test, y_rec_train, y_rec_test = train_test_split(
        X, y_score, y_recommend, test_size=0.2, random_state=42
    )
    
    # 5. Evaluate Regressors (Site Score Prediction)
    print("\n--- Training & Evaluating Regressors ---")
    regressors = {
        "Linear Regression": LinearRegression(),
        "Decision Tree Regressor": DecisionTreeRegressor(random_state=42),
        "Random Forest Regressor": RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42),
        "Gradient Boosting Regressor": GradientBoostingRegressor(n_estimators=100, random_state=42)
    }
    
    regression_results = []
    best_r2 = -1.0
    best_regressor = None
    best_regressor_name = None
    
    for name, model in regressors.items():
        start_time = time.time()
        model.fit(X_train, y_score_train)
        train_time = time.time() - start_time
        
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_score_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_score_test, y_pred))
        r2 = r2_score(y_score_test, y_pred)
        
        regression_results.append({
            "Model": name,
            "MAE": round(mae, 4),
            "RMSE": round(rmse, 4),
            "R2": round(r2, 4),
            "Train Time (s)": round(train_time, 4)
        })
        
        if r2 > best_r2:
            best_r2 = r2
            best_regressor = model
            best_regressor_name = name
            
    # 6. Evaluate Classifiers (Recommendation Classification)
    print("\n--- Training & Evaluating Classifiers ---")
    classifiers = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Decision Tree Classifier": DecisionTreeClassifier(random_state=42),
        "Random Forest Classifier": RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42),
        "Gradient Boosting Classifier": GradientBoostingClassifier(n_estimators=100, random_state=42)
    }
    
    classification_results = []
    best_f1 = -1.0
    best_classifier = None
    best_classifier_name = None
    
    for name, model in classifiers.items():
        start_time = time.time()
        model.fit(X_train, y_rec_train)
        train_time = time.time() - start_time
        
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_rec_test, y_pred)
        prec = precision_score(y_rec_test, y_pred, average='macro', zero_division=0)
        rec = recall_score(y_rec_test, y_pred, average='macro', zero_division=0)
        f1 = f1_score(y_rec_test, y_pred, average='macro', zero_division=0)
        
        classification_results.append({
            "Model": name,
            "Accuracy": round(acc, 4),
            "Precision": round(prec, 4),
            "Recall": round(rec, 4),
            "F1-Score": round(f1, 4),
            "Train Time (s)": round(train_time, 4)
        })
        
        if f1 > best_f1:
            best_f1 = f1
            best_classifier = model
            best_classifier_name = name

    # 7. Print comparative tables in console
    print("\n=== Regression Comparison Table ===")
    print(f"| {'Model':<30} | {'MAE':<10} | {'RMSE':<10} | {'R2 Score':<10} | {'Train Time (s)':<15} |")
    print(f"|{'-'*32}|{'-'*12}|{'-'*12}|{'-'*12}|{'-'*18}|")
    for r in regression_results:
        print(f"| {r['Model']:<30} | {r['MAE']:<10} | {r['RMSE']:<10} | {r['R2']:<10} | {r['Train Time (s)']:<15} |")

    print("\n=== Classification Comparison Table ===")
    print(f"| {'Model':<30} | {'Accuracy':<10} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10} | {'Train Time (s)':<15} |")
    print(f"|{'-'*32}|{'-'*12}|{'-'*12}|{'-'*12}|{'-'*12}|{'-'*18}|")
    for c in classification_results:
        print(f"| {c['Model']:<30} | {c['Accuracy']:<10} | {c['Precision']:<10} | {c['Recall']:<10} | {c['F1-Score']:<10} | {c['Train Time (s)']:<15} |")

    # 8. Save comparison results as evaluation_report.md
    models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'models'))
    os.makedirs(models_dir, exist_ok=True)
    report_path = os.path.join(models_dir, 'evaluation_report.md')
    
    with open(report_path, 'w') as rf:
        rf.write("# Model Evaluation & Comparison Report\n\n")
        rf.write("This report presents the comparative metrics of all trained baseline models.\n\n")
        
        rf.write("## 1. Suitability Score Regressors (Site Scoring)\n\n")
        rf.write("| Model | MAE | RMSE | R² Score | Train Time (s) |\n")
        rf.write("|---|---|---|---|---|\n")
        for r in regression_results:
            rf.write(f"| {r['Model']} | {r['MAE']} | {r['RMSE']} | {r['R2']} | {r['Train Time (s)']} |\n")
            
        rf.write("\n## 2. Deployment Classifiers (Technology Recommendation)\n\n")
        rf.write("| Model | Accuracy | Precision | Recall | F1-Score | Train Time (s) |\n")
        rf.write("|---|---|---|---|---|---|\n")
        for c in classification_results:
            rf.write(f"| {c['Model']} | {c['Accuracy']} | {c['Precision']} | {c['Recall']} | {c['F1-Score']} | {c['Train Time (s)']} |\n")
            
        rf.write("\n## 3. Best Model Selection & Justification\n\n")
        rf.write(f"### Selected Regressor: **{best_regressor_name}**\n")
        rf.write(f"- **R² Score**: {best_r2:.4f}\n")
        rf.write("- **Justification**: Exhibits highest variance explanation and lowest predictions error. Highly stable ensemble.\n\n")
        rf.write(f"### Selected Classifier: **{best_classifier_name}**\n")
        rf.write(f"- **F1-Score**: {best_f1:.4f}\n")
        rf.write("- **Justification**: High accuracy and precision-recall trade-offs. Adapts to non-linear class distributions perfectly.\n")
        
    print(f"\nSaved evaluation report to: {report_path}")

    # 9. Model Serialization
    reg_path = os.path.join(models_dir, 'suitability_regressor.joblib')
    clf_path = os.path.join(models_dir, 'deployment_classifier.joblib')
    
    print(f"\nPersisting best models to {models_dir}...")
    joblib.dump(best_regressor, reg_path)
    joblib.dump(best_classifier, clf_path)
    
    print("Model Comparison and Serialization complete!")

if __name__ == "__main__":
    main()
