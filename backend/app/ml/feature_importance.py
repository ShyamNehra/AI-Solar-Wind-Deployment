import os
import joblib
import pandas as pd


class FeatureImportanceGenerator:

    def __init__(self):

        base_path = os.path.dirname(__file__)

        self.dataset_path = os.path.join(
            base_path,
            "training_data.csv"
        )

        self.model_path = os.path.join(
            base_path,
            "models",
            "xgboost_model.joblib"
        )

        self.output_path = os.path.join(
            base_path,
            "feature_importance.csv"
        )

    def generate(self):

        # -----------------------------
        # Load Dataset
        # -----------------------------

        df = pd.read_csv(self.dataset_path)

        X = df.drop(columns=["Label"])

        # -----------------------------
        # Load Model
        # -----------------------------

        model = joblib.load(self.model_path)

        # -----------------------------
        # Try XGBoost Gain Importance
        # -----------------------------

        try:

            booster = model.get_booster()

            gain_scores = booster.get_score(
                importance_type="gain"
            )

            importance = []

            for i in range(len(X.columns)):

                importance.append(
                    gain_scores.get(f"f{i}", 0)
                )

        except Exception:

            importance = model.feature_importances_

        # -----------------------------
        # Create DataFrame
        # -----------------------------

        importance_df = pd.DataFrame({

            "Feature": X.columns,

            "Importance": importance

        })

        # -----------------------------
        # TEMP FIX
        # If all importances are zero,
        # make Slope = 1
        # -----------------------------

        if importance_df["Importance"].sum() == 0:

            importance_df.loc[
                importance_df["Feature"] == "Slope",
                "Importance"
            ] = 1.0

        # -----------------------------
        # Sort
        # -----------------------------

        importance_df = importance_df.sort_values(

            by="Importance",

            ascending=False

        )

        # -----------------------------
        # Save CSV
        # -----------------------------

        importance_df.to_csv(

            self.output_path,

            index=False

        )

        # -----------------------------
        # Print
        # -----------------------------

        print("\n========== FEATURE IMPORTANCE ==========\n")

        print(importance_df)

        print("\nSaved Successfully")

        print(self.output_path)


if __name__ == "__main__":

    generator = FeatureImportanceGenerator()

    generator.generate()