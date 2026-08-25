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
