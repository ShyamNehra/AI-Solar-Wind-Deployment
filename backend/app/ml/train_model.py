import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

from xgboost import XGBClassifier


class ModelTrainer:
    """
    Train both Random Forest and XGBoost models
    using prepared training_data.csv.
    """

    def __init__(self):

        current_dir = os.path.dirname(__file__)

        self.dataset_path = os.path.join(
            current_dir,
            "training_data.csv"
        )

        self.model_dir = os.path.join(
            current_dir,
            "models"
        )

        self.rf_model_path = os.path.join(
            self.model_dir,
            "random_forest_model.joblib"
        )

        self.xgb_model_path = os.path.join(
            self.model_dir,
            "xgboost_model.joblib"
        )

    def train(self):

        # -----------------------------------
        # Load dataset
        # -----------------------------------

        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(
                f"Dataset not found:\n{self.dataset_path}"
            )

        df = pd.read_csv(self.dataset_path)

        print("\nDataset loaded successfully.\n")
        print(df.head())

        # -----------------------------------
        # Convert Label
        # -----------------------------------

        df["Label"] = (
            df["Label"]
            .astype(str)
            .str.strip()
            .map(
                {
                    "Yes": 1,
                    "No": 0
                }
            )
        )

        df = df.dropna(subset=["Label"])

        df["Label"] = df["Label"].astype(int)

        # -----------------------------------
        # Features and Target
        # -----------------------------------

        X = df.drop(columns=["Label"])
        y = df["Label"]
        X = X.fillna(X.mean(numeric_only=True))
        X = X.fillna(0)
        # -----------------------------------
        # 70 / 15 / 15 Split
        # -----------------------------------

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

        # -----------------------------------
        # Random Forest
        # -----------------------------------

        rf_model = RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )

        rf_model.fit(
            X_train,
            y_train
        )

        rf_predictions = rf_model.predict(X_val)

        rf_accuracy = accuracy_score(
            y_val,
            rf_predictions
        )

        # -----------------------------------
        # XGBoost
        # -----------------------------------

        xgb_model = XGBClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42,
            eval_metric="logloss"
        )

        xgb_model.fit(
            X_train,
            y_train
        )

        xgb_predictions = xgb_model.predict(X_val)

        xgb_accuracy = accuracy_score(
            y_val,
            xgb_predictions
        )

        # -----------------------------------
        # Save Models
        # -----------------------------------

        os.makedirs(
            self.model_dir,
            exist_ok=True
        )

        joblib.dump(
            rf_model,
            self.rf_model_path
        )

        joblib.dump(
            xgb_model,
            self.xgb_model_path
        )

        # -----------------------------------
        # Results
        # -----------------------------------

        print("\n========== MODEL TRAINING ==========\n")

        print(f"Training Samples   : {len(X_train)}")
        print(f"Validation Samples : {len(X_val)}")
        print(f"Testing Samples    : {len(X_test)}\n")

        print(f"Random Forest Validation Accuracy : {rf_accuracy:.4f}")
        print(f"XGBoost Validation Accuracy       : {xgb_accuracy:.4f}\n")

        print("Models saved successfully.\n")

        print(f"Random Forest : {self.rf_model_path}")
        print(f"XGBoost       : {self.xgb_model_path}")


if __name__ == "__main__":

    trainer = ModelTrainer()

    trainer.train()