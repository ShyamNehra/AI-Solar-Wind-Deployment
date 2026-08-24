"""
Machine Learning Model Trainer supporting Multi-Model Training, Evaluation, Model Comparison, and Automatic Best Model Selection.
Integrates ModelTrainingPipeline, ModelEvaluator, ModelSelector, and ModelSerializer.
"""

from typing import Dict, Any, Tuple, Optional, Union, List
import numpy as np
import pandas as pd
import logging

from app.ml.training import ModelTrainingPipeline
from app.ml.evaluation import ModelEvaluator
from app.ml.selection import ModelSelector
from app.ml.serialization import ModelSerializer
from app.ml.preprocessing import MLPreprocessor
from app.ml.feature_selector import FeatureSelector

logger = logging.getLogger("ml.trainer")

class MLTrainer:
    """
    Orchestrates training multiple candidate models, evaluating them, comparing metrics,
    automatically selecting the best model, and preparing serializable artifacts.
    """

    def __init__(self):
        self.preprocessor = MLPreprocessor()
        self.feature_selector = FeatureSelector()
        self.evaluator = ModelEvaluator()
        self.selector = ModelSelector()
        self.serializer = ModelSerializer()

    def split_dataset(
        self, X: np.ndarray, y: pd.Series, train_ratio: float = 0.80, val_ratio: float = 0.10, test_ratio: float = 0.10, random_state: int = 42
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, pd.Series, pd.Series, pd.Series]:
        """
        Splits feature matrix X and target y into Train and Test/Val subsets.
        """
        from sklearn.model_selection import train_test_split
        test_plus_val_ratio = val_ratio + test_ratio
        if test_plus_val_ratio <= 0.0:
            test_plus_val_ratio = 0.20

        X_train, X_temp, y_train, y_temp = train_test_split(
            X, y, test_size=test_plus_val_ratio, random_state=random_state
        )
        if len(X_temp) > 1:
            X_val, X_test, y_val, y_test = train_test_split(
                X_temp, y_temp, test_size=0.5, random_state=random_state
            )
        else:
            X_val, X_test = X_temp, X_temp
            y_val, y_test = y_temp, y_temp

        return X_train, X_val, X_test, y_train, y_val, y_test

    def train_baseline(
        self,
        df: pd.DataFrame,
        target_variable: str = "solar_irradiance",
        model_type: str = "auto",
        algorithm: str = "random_forest",
        test_size: float = 0.2,
        random_state: int = 42,
        hyperparameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executes single model baseline training pipeline.
        """
        pipeline = ModelTrainingPipeline(random_state=random_state)
        res = pipeline.train_candidates(
            df=df,
            target_variable=target_variable,
            model_type=model_type,
            algorithms=[algorithm],
            test_size=test_size,
            hyperparameters={algorithm: hyperparameters} if hyperparameters else None
        )

        cand = res["candidates"][0]
        table = self.evaluator.create_comparison_table([cand], prediction_type=res["prediction_type"])
        row = table[0]

        return {
            "model": cand["model"],
            "preprocessor": res["preprocessor"],
            "prediction_type": res["prediction_type"],
            "algorithm": algorithm,
            "target_variable": target_variable,
            "feature_names": res["feature_names"],
            "feature_importance": cand["feature_importance"],
            "metrics": row["metrics"],
            "train_metrics": cand["train_metrics"],
            "model_behavior": f"Trained {row['model']} baseline. MAE: {row.get('mae', 'N/A')}, RMSE: {row.get('rmse', 'N/A')}, R2: {row.get('r2', 'N/A')}.",
            "sample_count": len(df),
            "training_time": cand["training_time"],
            "prediction_time": cand["prediction_time_ms"],
            "model_size": row["model_size"],
            "hyperparameters": hyperparameters or {},
        }

    def compare_baselines(
        self,
        df: pd.DataFrame,
        target_variable: str = "solar_irradiance",
        model_type: str = "auto",
        algorithms: Optional[List[str]] = None,
        random_state: int = 42,
        test_size: float = 0.2
    ) -> Dict[str, Any]:
        """
        Trains multiple candidate models, evaluates metrics, creates comparative JSON table,
        automatically selects best model using multi-criteria rules, and prepares serializable payload.
        """
        if algorithms is None or len(algorithms) == 0:
            algorithms = ["random_forest", "decision_tree", "gradient_boosting", "extra_trees", "linear"]

        pipeline = ModelTrainingPipeline(random_state=random_state)
        train_res = pipeline.train_candidates(
            df=df,
            target_variable=target_variable,
            model_type=model_type,
            algorithms=algorithms,
            test_size=test_size
        )

        candidates = train_res["candidates"]
        prediction_type = train_res["prediction_type"]

        # Create structured comparison table
        comparison_table = self.evaluator.create_comparison_table(candidates, prediction_type=prediction_type)

        # Automatically select best model
        winner_candidate, winner_row, selection_reason, ranking_score = self.selector.select_best_model(
            candidates=candidates,
            comparison_table=comparison_table,
            prediction_type=prediction_type
        )

        best_algo = winner_candidate["algorithm"]
        best_score = winner_row.get("r2", winner_row.get("accuracy", 0.0))

        best_artifact = {
            "model": winner_candidate["model"],
            "preprocessor": train_res["preprocessor"],
            "label_encoder": train_res.get("label_encoder"),
            "prediction_type": prediction_type,
            "algorithm": best_algo,
            "target_variable": target_variable,
            "feature_names": train_res["feature_names"],
            "feature_importance": winner_row["feature_importance"],
            "metrics": winner_row["metrics"],
            "model_behavior": selection_reason,
            "ranking_score": ranking_score,
            "sample_count": len(df),
            "training_time": winner_row["training_time"],
            "prediction_time": winner_row["prediction_time"],
            "model_size": winner_row["model_size"],
            "hyperparameters": winner_candidate.get("hyperparameters", {}),
            "comparison_table": comparison_table,
        }

        logger.info("Comparison completed: Best model selected is '%s' with ranking score %.2f", winner_row["model"], ranking_score)

        total_training_duration = round(sum(c.get("training_time", 0.0) for c in candidates), 4)

        return {
            "comparison_table": comparison_table,
            "selected_model": winner_row["model"],
            "selected_model_reason": selection_reason,
            "ranking_score": ranking_score,
            "best_algorithm": best_algo,
            "best_score": best_score,
            "best_model_artifact": best_artifact,
            "winner_candidate": winner_candidate,
            "winner_row": winner_row,
            "preprocessor": train_res["preprocessor"],
            "target_variable": target_variable,
            "prediction_type": prediction_type,
            "feature_names": train_res["feature_names"],
            "sample_count": len(df),
            "split_info": train_res["split_info"],
            "models_trained_count": len(candidates),
            "training_duration": total_training_duration
        }

