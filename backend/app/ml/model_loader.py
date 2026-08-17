import os
import joblib


class ModelLoader:
    """
    Loads the trained machine learning model once
    and reuses it for all predictions.
    """

    _model = None

    @classmethod
    def load_model(cls):
        """
        Load the model only once.
        """

        if cls._model is None:

            model_path = os.path.join(
                os.path.dirname(__file__),
                "models",
                "xgboost_model.joblib"
            )

            if not os.path.exists(model_path):
                raise FileNotFoundError(
                    f"Model not found:\n{model_path}"
                )

            cls._model = joblib.load(model_path)

            # Compatibility fix for models serialized
            # with older XGBoost versions.
            if hasattr(cls._model, "get_params"):
                try:
                    cls._model.use_label_encoder = None
                except Exception:
                    pass

            print("XGBoost model loaded successfully.")

        return cls._model
