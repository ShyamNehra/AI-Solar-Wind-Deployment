from app.evaluation.constraints import evaluate_all_constraints
from app.evaluation.scorer import calculate_suitability_score
from app.evaluation.recommendation import generate_recommendation

class SiteEvaluatorService:
    """Orchestrates the entire evaluation workflow pipeline for solar/wind properties."""

    @staticmethod
    def evaluate_site(features: dict) -> dict:
        """
        Runs a complete site assessment pipeline.
        
        Input: Feature dictionary containing solar, wind, slope, and proximity distances.
        Output: Structured evaluation matrix.
        """
        # Step 1: Constraint Verification Check
        is_viable, failed_reasons = evaluate_all_constraints(features)

        # Step 2: Calculate Weighted Numerical Score
        # (If a site fails a hard constraint, we force its score down to 0)
        overall_score = calculate_suitability_score(features) if is_viable else 0.0

        # Step 3: Map Score to Classifications & Recommendations
        recommendation = generate_recommendation(overall_score, is_viable)

        # Step 4: Assemble Final Unified Structural Dictionary
        return {
            "is_viable": is_viable,
            "failed_constraints": failed_reasons,
            "overall_score": overall_score,
            "recommendation": recommendation,
            "input_snapshot": features
        }