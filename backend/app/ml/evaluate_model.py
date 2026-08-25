from pathlib import Path
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)


class ModelEvaluator:

    def __init__(self):

        base_path = Path(__file__).parent

        self.dataset_path = base_path / "training_data.csv"

        self.rf_model_path = (
            base_path /
            "models" /
            "random_forest_model.joblib"
        )

        self.xgb_model_path = (
            base_path /
            "models" /
            "xgboost_model.joblib"
        )

    def evaluate(self):

        # --------------------------------
        # Load Dataset
        # --------------------------------

        df = pd.read_csv(self.dataset_path)

        df["Label"] = (
            df["Label"]
            .astype(str)
            .str.strip()
            .map({
                "Yes": 1,
                "No": 0
            })
        )

        df = df.dropna(subset=["Label"])

        X = df.drop(columns=["Label"])
        y = df["Label"]

        # --------------------------------
        # Handle Missing Values
        # --------------------------------

        X = X.fillna(X.mean(numeric_only=True))
        X = X.fillna(0)

        # --------------------------------
        # Same Split as train_model.py
        # 70 / 15 / 15
        # --------------------------------

        X_train, X_temp, y_train, y_temp = train_test_split(
            X,
            y,
            test_size=0.30,
            random_state=42,
            stratify=y
        )

        X_val, X_test, y_val, y_test = train_test_split(
            X_temp,
            y_temp,
            test_size=0.50,
            random_state=42,
            stratify=y_temp
        )

        # Safety

        X_val = X_val.fillna(0)
        X_test = X_test.fillna(0)

        # --------------------------------
        # Load Models
        # --------------------------------

        rf_model = joblib.load(self.rf_model_path)

        xgb_model = joblib.load(self.xgb_model_path)

        # --------------------------------
        # Predictions
        # --------------------------------

        rf_pred = rf_model.predict(X_val)

        xgb_pred = xgb_model.predict(X_val)

        # --------------------------------
        # Metrics Function
        # --------------------------------

        def calculate_metrics(y_true, y_pred):

            return {
                "Accuracy": accuracy_score(y_true, y_pred),
                "Precision": precision_score(y_true, y_pred),
                "Recall": recall_score(y_true, y_pred),
                "F1 Score": f1_score(y_true, y_pred)
            }

        rf_metrics = calculate_metrics(
            y_val,
            rf_pred
        )

        xgb_metrics = calculate_metrics(
            y_val,
            xgb_pred
        )

        # --------------------------------
        # Comparison Table
        # --------------------------------

        comparison = pd.DataFrame({

            "Metric": [
                "Accuracy",
                "Precision",
                "Recall",
                "F1 Score"
            ],

            "Random Forest": [
                rf_metrics["Accuracy"],
                rf_metrics["Precision"],
                rf_metrics["Recall"],
                rf_metrics["F1 Score"]
            ],

            "XGBoost": [
                xgb_metrics["Accuracy"],
                xgb_metrics["Precision"],
                xgb_metrics["Recall"],
                xgb_metrics["F1 Score"]
            ]

        })

        print("\n========== MODEL COMPARISON ==========\n")

        print(comparison)

        if xgb_metrics["Accuracy"] >= rf_metrics["Accuracy"]:
            print("\nBest Model : XGBoost")
        else:
            print("\nBest Model : Random Forest")


if __name__ == "__main__":

    evaluator = ModelEvaluator()

    evaluator.evaluate()