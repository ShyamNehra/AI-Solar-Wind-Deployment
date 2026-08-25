import os
import joblib
import pandas as pd


class MLPredictionService:

    def __init__(self):

        model_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "ml",
            "models",
            "xgboost_model.joblib"
        )

        self.model = joblib.load(
            os.path.abspath(model_path)
        )

    def predict(self, features: dict):

        df = pd.DataFrame([features])

        prediction = self.model.predict(df)[0]

        return {
            "prediction": "Suitable"
            if prediction == 1
            else "Not Suitable"
        }