"""
Utility functions for Technical Feasibility Validation Engine.
Generates human-readable constraint summaries and engineering decision recommendations.
"""

from typing import List, Dict, Any, Tuple


def generate_constraint_summary(
    hard_passed: bool,
    violations: List[str],
    soft_scores: Dict[str, float],
    score: float,
    rating: str
) -> List[str]:
    """
    Builds bulleted human-readable constraint summary sentences.
    """
    summary: List[str] = []

    if not hard_passed:
        summary.append(f"CRITICAL VIOLATION: Site fails mandatory engineering constraints ({', '.join(violations)}).")
        summary.append("Immediate rejection — Site cannot be developed for renewable energy deployment.")
        return summary

    summary.append("No critical hard constraint violations detected.")

    # Infrastructure & Road summary
    infra = soft_scores.get("infrastructure", 80.0)
    if infra >= 85.0:
        summary.append("Excellent road and power grid infrastructure proximity.")
    elif infra >= 60.0:
        summary.append("Moderate infrastructure availability requiring standard grid interconnection.")
    else:
        summary.append("Poor infrastructure proximity — high capital expenditure required for road and grid access.")

    # Terrain summary
    terrain = soft_scores.get("terrain", 80.0)
    if terrain >= 85.0:
        summary.append("Favorable flat/gentle terrain suitable for construction.")
    elif terrain >= 60.0:
        summary.append("Moderate terrain slope — standard foundation civil engineering required.")
    else:
        summary.append("Challenging terrain with steep slopes — complex civil earthworks expected.")

    # Overall rating summary
    summary.append(f"Overall technical feasibility evaluated as {rating} ({score:.1f}%).")

    return summary

def determine_decision_and_recommendation(
    hard_passed: bool,
    violations: List[str],
    score: float,
    rating: str,
    ml_prediction: str = "Hybrid"
) -> Tuple[str, str]:
    """
    Determines engineering decision ('Approved' | 'Feasible for Deployment' | 'NOT FEASIBLE')
    and engineering recommendation text.
    """
    if not hard_passed:
        decision = "NOT FEASIBLE"
        rec = f"Site rejected due to critical hard constraint violations: {', '.join(violations)}. ML prediction ('{ml_prediction}') cannot override engineering constraints."
        return decision, rec

    if score >= 75.0:
        decision = "Approved"
        rec = f"Site is Approved and Feasible for Deployment ({ml_prediction} recommendation supported with {rating} engineering feasibility score of {score:.1f}%)."
    elif score >= 60.0:
        decision = "Feasible with Conditions"
        rec = f"Site is Feasible with Conditions (Moderate feasibility score {score:.1f}%). Mitigation required for infrastructure/terrain constraints."
    else:
        decision = "NOT FEASIBLE"
        rec = f"Site rejected due to poor technical feasibility score ({score:.1f}% < 60.0%). Infrastructure or terrain costs exceed feasibility thresholds."

    return decision, rec
