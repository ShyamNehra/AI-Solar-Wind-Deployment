"""
Master Technical Feasibility Validation Engine.
Evaluates engineering feasibility AFTER machine learning prediction and BEFORE final deployment recommendation.
Enforces hard constraint rejection, soft constraint weighted scoring, logging, and engineering decision output.
"""

import logging
from typing import Dict, Any, Optional

from app.services.feasibility.models import (
    HardConstraintResult,
    SoftConstraintResult,
    FeasibilityResult
)
from app.services.feasibility.hard_constraints import HardConstraintValidator
from app.services.feasibility.soft_constraints import SoftConstraintScorer
from app.services.feasibility.utils import (
    generate_constraint_summary,
    determine_decision_and_recommendation
)

logger = logging.getLogger("feasibility.engine")


class TechnicalFeasibilityEngine:
    """
    Reusable, independent Technical Feasibility Validation Engine.
    Evaluates engineering feasibility after ML prediction and before final deployment decision.
    """

    def __init__(self):
        self.hard_validator = HardConstraintValidator()
        self.soft_scorer = SoftConstraintScorer()

    def evaluate_feasibility(
        self,
        features: Dict[str, Any],
        ml_prediction: Optional[str] = "Hybrid",
        max_slope_degrees: float = 35.0
    ) -> FeasibilityResult:
        """
        Runs complete technical feasibility evaluation pipeline:
        1. Hard Constraint Validation
        2. Soft Constraint Scoring
        3. Composite Score & Rating Calculation
        4. Engineering Decision Determination
        """
        logger.info("Feasibility Started: Evaluating site features for target prediction '%s'", ml_prediction)

        # Step 1: Hard Constraint Validation
        logger.info("Hard Constraint Validation: Checking mandatory engineering thresholds")
        hard_res = self.hard_validator.validate(features, max_slope_degrees=max_slope_degrees)

        # Step 2: Soft Constraint Scoring
        logger.info("Soft Constraint Scoring: Calculating weighted engineering scores")
        raw_score, rating, soft_dict = self.soft_scorer.evaluate(features)

        # Step 3: Handle Hard Constraint Rejection vs Soft Score Integration
        if not hard_res.passed:
            logger.warning(
                "Hard Constraint Violation Detected: Site rejected due to %s",
                ", ".join(hard_res.violations)
            )
            technical_feasibility = False
            feasibility_score = 0.0
            feasibility_rating = "Poor (Rejected)"
        else:
            technical_feasibility = raw_score >= 60.0
            feasibility_score = raw_score
            feasibility_rating = rating

        # Step 4: Engineering Decision
        decision, recommendation = determine_decision_and_recommendation(
            hard_passed=hard_res.passed,
            violations=hard_res.violations,
            score=feasibility_score,
            rating=feasibility_rating,
            ml_prediction=ml_prediction or "Hybrid"
        )

        logger.info(
            "Engineering Decision: '%s' (Technical Feasibility: %s, Score: %.1f%%)",
            decision, technical_feasibility, feasibility_score
        )

        summary_lines = generate_constraint_summary(
            hard_passed=hard_res.passed,
            violations=hard_res.violations,
            soft_scores=soft_dict,
            score=feasibility_score,
            rating=feasibility_rating
        )

        return FeasibilityResult(
            technical_feasibility=technical_feasibility,
            feasibility_score=feasibility_score,
            feasibility_rating=feasibility_rating,
            engineering_decision=decision,
            engineering_recommendation=recommendation,
            hard_constraints=hard_res,
            soft_constraints=soft_dict,
            constraint_summary=summary_lines
        )
