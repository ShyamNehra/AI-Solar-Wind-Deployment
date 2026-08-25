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
"""
Inference & Prediction Orchestration Service.
Uses ProductionPredictor and ModelInferenceModule for single-load cached joblib model management.
"""

from typing import Dict, Any, Optional, Union
import pandas as pd

from app.ml.inference import ModelInferenceModule
from app.ml.prediction import ProductionPredictor
from app.ml.schemas import FeatureVector


class MLPredictor:
    """
    Inference service orchestrator leveraging ProductionPredictor and ModelInferenceModule.
    """

    def __init__(self, models_dir: Optional[str] = None):
        self.inference_module = ModelInferenceModule(models_dir)
        self.predictor = ProductionPredictor(models_dir)

    def get_or_train_model(
        self, prediction_type: str = "regression", db: Any = None, target_col: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieves cached model artifact from memory or disk if available.
        """
        return self.predictor.load_model()

    def predict(
        self,
        feature_data: Union[Dict[str, Any], FeatureVector, pd.DataFrame],
        prediction_type: str = "regression",
        db: Any = None
    ) -> Dict[str, Any]:
        """
        Executes prediction pipeline via ProductionPredictor.
        """
        return self.predictor.predict(
            feature_data=feature_data,
            prediction_type=prediction_type
        )
