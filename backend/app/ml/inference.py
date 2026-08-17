from app.ml.predictor import Predictor


class ModelInference:
    """
    Handles ML inference for the application.

    This class acts as the interface between the backend
    services and the machine learning prediction pipeline.
    """

    def __init__(self):
        self.predictor = Predictor()

    def predict_site(self, features: list):
        """
        Predict site suitability.

        Parameters
        ----------
        features : list
            Ordered feature values.

        Returns
        -------
        Prediction produced by the ML model.
        """
        return self.predictor.predict(features)