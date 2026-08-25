"""
Automatic Model Selection Module.
Evaluates candidate model performance across R², MAE, RMSE, Accuracy/F1, training speed, inference latency,
and model complexity to pick the optimal deployment candidate.
"""

import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger("ml.selection")


class ModelSelector:
    """
    Automatic best model selection engine supporting composite multi-criteria scoring
    across Prediction Performance, Training Time, Inference Speed, Complexity,
    Deployment Simplicity, and Memory Usage.
    """

    def select_best_model(
        self,
        candidates: List[Dict[str, Any]],
        comparison_table: List[Dict[str, Any]],
        prediction_type: str = "regression"
    ) -> Tuple[Dict[str, Any], Dict[str, Any], str, float]:
        """
        Selects winner model candidate based on composite multi-criteria ranking score.
        Returns Tuple of (winner_candidate_dict, winner_comparison_row, selection_reason_summary, ranking_score).
        """
        if not candidates or not comparison_table:
            raise ValueError("Candidates list or comparison table is empty.")

        # Extract bounds for normalization
        train_times = [r.get("training_time", 0.01) for r in comparison_table]
        pred_times = [r.get("prediction_time", 0.1) for r in comparison_table]
        mem_sizes = [r.get("model_size_kb", 10.0) for r in comparison_table]

        max_train = max(train_times) if train_times and max(train_times) > 0 else 1.0
        max_pred = max(pred_times) if pred_times and max(pred_times) > 0 else 1.0
        max_mem = max(mem_sizes) if mem_sizes and max(mem_sizes) > 0 else 100.0

        best_score = -9999.0
        winner_candidate = candidates[0]
        winner_row = comparison_table[0]

        for cand, row in zip(candidates, comparison_table):
            algo_key = cand.get("algorithm", "random_forest")
            train_t = row.get("training_time", 0.01)
            pred_t = row.get("prediction_time", 0.1)
            size_kb = row.get("model_size_kb", 10.0)

            # 1. Performance score (45% weight)
            if prediction_type == "classification":
                acc = row.get("accuracy", 0.0)
                f1 = row.get("f1_score", 0.0)
                perf_score = (acc * 0.6) + (f1 * 0.4)
            else:
                r2 = max(0.0, row.get("r2", row.get("r2_score", 0.0)))
                rmse = row.get("rmse", 1.0)
                mae = row.get("mae", 1.0)
                perf_score = r2

            # 2. Speed score: training & inference time (20% weight)
            speed_train_norm = 1.0 - (train_t / (max_train + 1e-6))
            speed_pred_norm = 1.0 - (pred_t / (max_pred + 1e-6))
            speed_score = (speed_train_norm * 0.5) + (speed_pred_norm * 0.5)

            # 3. Model Complexity & Deployment Simplicity (20% weight)
            if algo_key in ["linear", "linear_regression", "logistic_regression"]:
                simplicity_score = 1.0
            elif algo_key in ["decision_tree"]:
                simplicity_score = 0.85
            elif algo_key in ["random_forest", "extra_trees"]:
                simplicity_score = 0.70
            elif algo_key in ["gradient_boosting", "xgboost"]:
                simplicity_score = 0.65
            else:
                simplicity_score = 0.60

            # 4. Memory score (15% weight)
            mem_score = 1.0 - (size_kb / (max_mem + 1e-6))

            # Composite weighted ranking score (0.0 to 100.0)
            composite_val = (
                (perf_score * 0.45) +
                (speed_score * 0.20) +
                (simplicity_score * 0.20) +
                (mem_score * 0.15)
            ) * 100.0

            ranking_score = round(composite_val, 2)
            row["ranking_score"] = ranking_score
            cand["ranking_score"] = ranking_score

            if composite_val > best_score:
                best_score = composite_val
                winner_candidate = cand
                winner_row = row

        final_ranking_score = round(best_score, 2)
        selected_name = winner_row.get("model", winner_candidate["algorithm"])

        if prediction_type == "classification":
            acc_val = winner_row.get("accuracy", 0.0)
            f1_val = winner_row.get("f1_score", 0.0)
            pred_speed = winner_row.get("prediction_time", 0.0)
            reason_str = (
                f"Selected {selected_name} based on multi-criteria ranking score ({final_ranking_score}/100), "
                f"Accuracy ({acc_val:.4f}), F1 Score ({f1_val:.4f}), fast inference ({pred_speed:.2f}ms), "
                f"low memory footprint, and high deployment simplicity."
            )
        else:
            r2_val = winner_row.get("r2", winner_row.get("r2_score", 0.0))
            rmse_val = winner_row.get("rmse", 0.0)
            mae_val = winner_row.get("mae", 0.0)
            pred_speed = winner_row.get("prediction_time", 0.0)
            reason_str = (
                f"Selected {selected_name} based on multi-criteria ranking score ({final_ranking_score}/100), "
                f"R² score ({r2_val:.4f}), low RMSE ({rmse_val:.4f}), low MAE ({mae_val:.4f}), "
                f"fast inference speed ({pred_speed:.2f}ms), and optimal complexity for production deployment."
            )

        winner_row["selection_reason"] = reason_str
        logger.info("Best Model Selected: '%s' (Score: %.2f). Reason: %s", selected_name, final_ranking_score, reason_str)

        return winner_candidate, winner_row, reason_str, final_ranking_score

