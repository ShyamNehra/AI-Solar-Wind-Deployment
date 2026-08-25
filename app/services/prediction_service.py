import os
import json
import joblib

class PredictionService:
    """
    Service responsible for loading ML models and executing inference.
    Gracefully handles missing model files to prevent FastAPI startup crashes
    and uses the persisted feature schema to guarantee correct feature alignment.
    """

    def __init__(self):
        self.models_loaded = False
        self.load_error = None
        self._regressor = None
        self._classifier = None
        self._models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../ml/models'))
        self._schema_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../ml/feature_schema.json'))
        self._feature_cols = []

        self.load_schema()
        self.load_models()

    def load_schema(self):
        """
        Load the feature ordering schema from feature_schema.json.
        """
        try:
            if os.path.exists(self._schema_path):
                with open(self._schema_path, 'r') as f:
                    self._feature_cols = json.load(f)
            else:
                self._feature_cols = [
                    "solar_irradiance", "wind_speed", "temperature", "humidity",
                    "elevation", "slope", "distance_to_road", "distance_to_grid",
                    "protected_area_distance", "environmental_impact_level",
                    "land_cost_per_acre", "grid_connection_cost"
                ]
        except Exception as e:
            self._feature_cols = []

    def load_models(self):
        """
        Attempt to load serialized best baseline models.
        """
        reg_path = os.path.join(self._models_dir, 'suitability_regressor.joblib')
        clf_path = os.path.join(self._models_dir, 'deployment_classifier.joblib')

        if not os.path.exists(reg_path) or not os.path.exists(clf_path):
            self.models_loaded = False
            self.load_error = (
                "ML model files are missing. Please run the model training pipeline "
                "first using: py -3.12 app/ml/train.py"
            )
            return

        try:
            self._regressor = joblib.load(reg_path)
            self._classifier = joblib.load(clf_path)
            self.models_loaded = True
            self.load_error = None
        except Exception as e:
            self.models_loaded = False
            self.load_error = f"Failed to load ML models due to error: {str(e)}"

    def predict_suitability_score(self, site_data: dict) -> float:
        """
        Predict site suitability score using the loaded regressor model.
        """
        if not self.models_loaded:
            raise RuntimeError(self.load_error)

        # Align features dynamically using feature_schema.json ordering
        features = [float(site_data.get(col, 0.0)) for col in self._feature_cols]
        prediction = self._regressor.predict([features])[0]
        return round(float(prediction), 2)

    def predict_deployment_recommendation(self, site_data: dict) -> str:
        """
        Predict technology deployment recommendation using the loaded classifier model.
        """
        if not self.models_loaded:
            raise RuntimeError(self.load_error)

        # Align features dynamically using feature_schema.json ordering
        features = [float(site_data.get(col, 0.0)) for col in self._feature_cols]
        prediction = self._classifier.predict([features])[0]
        return str(prediction)

    def get_feature_importance_regressor(self) -> list[dict]:
        """
        Get the Top 3 feature importances for the regressor model in descending order.
        """
        if not self.models_loaded:
            raise RuntimeError(self.load_error)

        importances = self._regressor.feature_importances_
        feature_imp = [
            {"feature": col, "importance": round(float(imp), 4)}
            for col, imp in zip(self._feature_cols, importances)
        ]
        feature_imp.sort(key=lambda x: x["importance"], reverse=True)
        return feature_imp[:3]

    def get_feature_importance_classifier(self) -> list[dict]:
        """
        Get the Top 3 feature importances for the classifier model in descending order.
        """
        if not self.models_loaded:
            raise RuntimeError(self.load_error)

        importances = self._classifier.feature_importances_
        feature_imp = [
            {"feature": col, "importance": round(float(imp), 4)}
            for col, imp in zip(self._feature_cols, importances)
        ]
        feature_imp.sort(key=lambda x: x["importance"], reverse=True)
        return feature_imp[:3]
