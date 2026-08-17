import os
import joblib
import pandas as pd
import xgboost as xgb


class Predictor:

    _model = None

    def __init__(self):

        base_path = os.path.dirname(__file__)

        self.model_path = os.path.join(
            base_path,
            "models",
            "xgboost_model.joblib"
        )

        self.feature_path = os.path.join(
            base_path,
            "feature_importance.csv"
        )

        if Predictor._model is None:

            Predictor._model = joblib.load(
                self.model_path
            )

            print("XGBoost model loaded successfully.")

    def predict(self, features):

        feature_names = [
            "Slope",
            "Elevation",
            "TurbulenceIntensity",
            "Yearly-AirTemperature",
            "Yearly-RelativeHumidity",
            "Yearly-Precipitation",
            "Yearly-WindSpeed",
            "Yearly-WindGustSpeed",
            "Yearly-AirPressure",
            "AnnualSolarIrradiance",
            "AverageNDVI",
            "AverageNDBI",
            "AverageNDWI",
            "AverageLST",
            "AverageCityElevation",
            "AverageDistrictPopulation",
            "AverageDistrictArea"
        ]

        X = pd.DataFrame(
            [features],
            columns=feature_names
        )

        # -------------------------------------------------
        # Use the underlying Booster directly.
        # This avoids compatibility problems in the old
        # XGBClassifier sklearn wrapper.
        # -------------------------------------------------

        booster = Predictor._model.get_booster()

        dmatrix = xgb.DMatrix(
            X,
            feature_names=feature_names
        )

        probabilities = booster.predict(dmatrix)

        probability = float(probabilities[0])

        prediction = 1 if probability >= 0.5 else 0

        label = (
            "Suitable"
            if prediction == 1
            else "Not Suitable"
        )

        # -------------------------------------------------
        # Top 3 important features
        # -------------------------------------------------

        importance = pd.read_csv(
            self.feature_path
        )

        top3 = importance.head(3)["Feature"].tolist()

        explanation = (
            "Prediction mainly influenced by: "
            + ", ".join(top3)
        )

        return {
            "prediction": prediction,
            "label": label,
            "probability": probability,
            "important_features": top3,
            "explanation": explanation
        }