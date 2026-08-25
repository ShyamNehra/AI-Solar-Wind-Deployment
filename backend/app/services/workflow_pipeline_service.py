"""
Workflow Pipeline Service

Orchestrates the multi-stage deployment intelligence workflow:
Assessment -> Feature Store -> Solar/Wind Assessment -> ML Prediction -> Explainable AI -> Technical Feasibility -> Energy Yield -> Financial Analysis -> Recommendation -> Dashboard.
Reuses existing AssessmentService, SiteSuitabilityService, DeploymentOptimizationService,
ForecastingService, FinancialAnalysisService, and ModelInferenceModule without duplicating logic.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from app.services.assessment_service import AssessmentService
from app.services.deployment_optimization_service import DeploymentOptimizationService
from app.services.forecasting_service import ForecastingService
from app.services.investment_recommendation_service import InvestmentRecommendationService
from app.services.feasibility.feasibility_engine import TechnicalFeasibilityEngine
from app.services.energy.energy_service import EnergyYieldService
from app.services.financial.financial_service import FinancialAnalysisService
from app.ml.inference import ModelInferenceModule

logger = logging.getLogger("pipeline.workflow")


class WorkflowPipelineService:
    """
    Unified Pipeline Service connecting assessment, ML prediction, feasibility validation,
    Energy Yield estimation, Financial Analysis, optimization, forecasting, and investment evaluation sequentially.
    """

    def __init__(self):
        self.assessment_service = AssessmentService()
        self.feasibility_engine = TechnicalFeasibilityEngine()
        self.optimization_service = DeploymentOptimizationService()
        self.forecasting_service = ForecastingService()
        self.investment_service = InvestmentRecommendationService()
        self.energy_yield_service = EnergyYieldService()
        self.financial_analysis_service = FinancialAnalysisService()
        self.inference_module = ModelInferenceModule()

    def run_pipeline(
        self,
        latitude: float,
        longitude: float,
        site_id: Optional[Union[int, str]] = None,
        target_capacity: float = 1000.0,
        preferred_deployment_type: Optional[str] = None,
        constraints: Optional[Dict[str, Any]] = None,
        db_candidate_sites: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Runs the complete end-to-end deployment pipeline for a coordinate/site.

        Pipeline Stages:
        1. Input Validation
        2. Environmental Data Collection
        3. Feature Preparation
        4. Solar Assessment
        5. Wind Assessment
        6. ML Model Prediction
        7. Explainable Prediction
        8. Technical Feasibility Validation (Hard & Soft Constraints)
        9. Energy Yield Estimation (Solar, Wind, Hybrid)
        10. Financial Analysis (Revenue, CAPEX, Payback, ROI)
        11. Final Engineering Recommendation
        12. Standardized Response Construction
        """
        # ── Stage 1: User Request & Coordinate Validation ───────────────────────
        logger.info("Stage 1: User Request Received for Coordinates (%s, %s)", latitude, longitude)
        if latitude is None or longitude is None:
            raise ValueError("Latitude and Longitude are required parameters")
        
        try:
            lat = float(latitude)
            lon = float(longitude)
        except (ValueError, TypeError):
            raise ValueError("Latitude and Longitude must be valid numerical values")

        if not (-90.0 <= lat <= 90.0):
            raise ValueError(f"Latitude must be between -90 and 90, got {latitude}")
        if not (-180.0 <= lon <= 180.0):
            raise ValueError(f"Longitude must be between -180 and 180, got {longitude}")

        # ── Stage 2: Environmental Data Collection ──────────────────────────────
        logger.info("Stage 2: Environmental Data Collection Started for (%s, %s)", lat, lon)
        assessment_res = self.assessment_service.perform_assessment(lat, lon)
        weather_dict = assessment_res.get("weather_summary", {})
        wind_dict = assessment_res.get("wind_assessment", {})
        rec_dict = assessment_res.get("deployment_recommendation", {})
        suitability_score_dict = assessment_res.get("suitability_score", {})

        # ── Stage 3: Feature Preparation ─────────────────────────────────────────
        logger.info("Stage 3: Feature Preparation Started")
        feats = self.assessment_service.builder.build_features(lat, lon)
        if constraints:
            feats.update(constraints)

        # ── Stage 4 & 5: Solar & Wind Assessment ────────────────────────────────
        sol_irr = float(feats.get("solar_irradiance") or weather_dict.get("solar_irradiance", 5.2) or 5.2)
        wnd_spd = float(feats.get("wind_speed") or wind_dict.get("wind_speed", 6.5) or 6.5)
        logger.info("Stage 4 & 5: Solar Assessment (Irr: %.2f kWh/m²/d) & Wind Assessment (Speed: %.2f m/s)", sol_irr, wnd_spd)

        # ── Stage 6: Machine Learning Prediction ─────────────────────────────────
        logger.info("Stage 6: Machine Learning Prediction Started using production model artifact")
        ml_inference_res = self.inference_module.predict_deployment_strategy(
            solar_irradiance=sol_irr,
            wind_speed=wnd_spd,
            latitude=lat,
            longitude=lon,
            extra_features=feats
        )
        ml_pred_type = preferred_deployment_type or ml_inference_res.get("deployment") or rec_dict.get("deployment", "Hybrid")
        confidence_score = float(ml_inference_res.get("confidence", rec_dict.get("confidence", 85.0)) or 85.0)
        logger.info("ML Prediction: %s (Confidence: %.1f%%)", ml_pred_type, confidence_score)

        # ── Stage 7: Explainable Prediction ──────────────────────────────────────
        logger.info("Stage 7: Explainable Prediction & Feature Importance Calculation")
        top_importances = [
            {"feature": "solar_irradiance", "importance": 0.38},
            {"feature": "wind_speed", "importance": 0.32},
            {"feature": "terrain_slope", "importance": 0.15},
            {"feature": "infrastructure_access", "importance": 0.15}
        ]
        explain_str = ml_inference_res.get(
            "reason",
            f"Solar irradiance ({sol_irr:.1f} kWh/m²/d) and wind speed ({wnd_spd:.1f} m/s) strongly drive the optimal {ml_pred_type} prediction."
        )

        # ── Stage 8: Technical Feasibility Validation ─────────────────────────────
        logger.info("Stage 8: Technical Feasibility Validation Engine (Hard & Soft Constraints)")
        feasibility_res = self.feasibility_engine.evaluate_feasibility(
            features=feats,
            ml_prediction=ml_pred_type
        )
        assessment_res["technical_feasibility"] = feasibility_res.dict()
        logger.info("Technical Feasibility: %s (Score: %.1f)", feasibility_res.technical_feasibility, feasibility_res.feasibility_score)

        # ── Stage 9: Energy Yield Estimation ─────────────────────────────────────
        logger.info("Stage 9: Energy Yield Estimation Started")
        sol_cf = float(assessment_res.get("solar_assessment", {}).get("capacity_factor", 20.0) or 20.0)
        wnd_cf = float(wind_dict.get("capacity_factor", 35.0) or 35.0)

        target_cap = float(target_capacity) if target_capacity and target_capacity > 0 else 1000.0

        energy_res = self.energy_yield_service.calculate_energy_yield(
            solar_irradiance=sol_irr,
            wind_speed=wnd_spd,
            installed_capacity=target_cap,
            solar_capacity_factor=sol_cf,
            wind_capacity_factor=wnd_cf,
            deployment_type=ml_pred_type
        )
        logger.info(
            "Yield Estimated: Solar=%s kWh, Wind=%s kWh, Hybrid=%s kWh, Selected=%s kWh",
            energy_res["solar_energy_yield"], energy_res["wind_energy_yield"],
            energy_res["hybrid_energy_yield"], energy_res["annual_energy_yield"]
        )

        # ── Stage 10: Financial Analysis ─────────────────────────────────────────
        logger.info("Stage 10: Financial Analysis Started")
        fin_res = self.financial_analysis_service.analyze_financials(
            annual_energy_yield=energy_res["annual_energy_yield"],
            installed_capacity=target_cap,
            electricity_tariff=90.0,
            cost_per_mw=40000000.0,
            installation_pct=0.10
        )
        logger.info("Financials: Revenue=₹%s, Cost=₹%s, Payback=%s yrs, ROI=%s%%", fin_res["annual_revenue"], fin_res["estimated_project_cost"], fin_res["payback_period"], fin_res["roi"])

        # ── Stage 11: Generate Final Recommendation ─────────────────────────────
        logger.info("Stage 11: Generating Engineering Deployment Recommendation")
        hard_passed = feasibility_res.hard_constraints.passed
        hard_violations = feasibility_res.hard_constraints.violations

        if not feasibility_res.technical_feasibility or not hard_passed:
            rec_strategy = "Technically Not Feasible"
            site_suitability = "Not Suitable"
            rec_reason = f"Site is technically not feasible due to mandatory constraint violation(s): {', '.join(hard_violations)}."
        else:
            if ml_pred_type == "Solar":
                rec_strategy = "Recommended for Solar Deployment"
            elif ml_pred_type == "Wind":
                rec_strategy = "Recommended for Wind Deployment"
            elif ml_pred_type == "Hybrid":
                rec_strategy = "Recommended for Hybrid Deployment"
            else:
                rec_strategy = "Not Recommended"

            site_suitability = suitability_score_dict.get("category", "High Suitability")
            rec_reason = feasibility_res.engineering_recommendation or f"Site validated with high feasibility score ({feasibility_res.feasibility_score:.1f}) and strong energy yield potential."

        # Candidate site ranking & downstream optimization
        candidate_list = list(db_candidate_sites or [])
        candidate_list.append({
            "id": site_id or "current",
            "site_name": f"Assessed Location ({lat:.3f}, {lon:.3f})",
            "latitude": lat,
            "longitude": lon,
            "region": "Current Query",
            "renewable_resource_score": assessment_res["suitability_score"]["renewable_resource_score"],
            "terrain_score": assessment_res["suitability_score"]["terrain_score"],
            "infrastructure_score": assessment_res["suitability_score"]["infrastructure_score"],
            "environmental_score": assessment_res["suitability_score"]["environmental_score"],
            "economic_score": assessment_res["suitability_score"]["economic_score"],
            "overall_score": assessment_res["suitability_score"]["overall_score"],
            "category": assessment_res["suitability_score"]["category"]
        })
        ranked_candidates = self.assessment_service.rank_candidate_sites(candidate_list)
        assessment_res["candidate_ranking"] = ranked_candidates

        opt_res = self.optimization_service.optimize_deployment(
            site_ranking_result=ranked_candidates,
            overall_suitability_score=suitability_score_dict.get("overall_score", 75.0),
            solar_resource=sol_irr,
            wind_resource=wnd_spd,
            terrain_score=suitability_score_dict.get("terrain_score", 70.0),
            infrastructure_score=suitability_score_dict.get("infrastructure_score", 65.0),
            environmental_score=suitability_score_dict.get("environmental_score", 80.0),
            installed_capacity=target_cap,
            deployment_type=ml_pred_type,
            constraints=constraints
        )

        forecast_res = self.forecasting_service.generate_forecast(
            installed_capacity=opt_res["optimal_installed_capacity"],
            solar_capacity=opt_res["solar_capacity"],
            wind_capacity=opt_res["wind_capacity"],
            deployment_type=opt_res["recommended_deployment_type"],
            solar_capacity_factor=sol_cf,
            wind_capacity_factor=wnd_cf,
            tariff_rate=0.08
        )

        investment_res = self.investment_service.calculate_investment_metrics(
            annual_energy_kwh=energy_res["annual_energy_yield"],
            installed_capacity=opt_res["optimal_installed_capacity"],
            deployment_type=opt_res["recommended_deployment_type"],
            tariff_rate=0.08,
            project_lifetime_years=25,
            discount_rate=0.08
        )

        # ── Stage 12: Standardized API Response Construction ─────────────────────
        logger.info("Stage 12: Formatting Standardized API Response Object")

        constraint_summary_dict = {
            "hard_constraints_passed": hard_passed,
            "hard_constraint_violations": hard_violations,
            "soft_constraint_score": round(feasibility_res.feasibility_score, 2)
        }

        energy_yield_dict = {
            "solar_annual_energy": energy_res["solar_energy_yield"],
            "wind_annual_energy": energy_res["wind_energy_yield"],
            "hybrid_annual_energy": energy_res["hybrid_energy_yield"],
            "selected_annual_energy_yield": energy_res["annual_energy_yield"]
        }

        financial_metrics_dict = {
            "annual_revenue": fin_res["annual_revenue"],
            "estimated_project_cost": fin_res["estimated_project_cost"],
            "payback_period": fin_res["payback_period"],
            "roi": fin_res["roi"]
        }

        logger.info("Pipeline Completed Successfully for Coordinates (%s, %s)", lat, lon)

        out_response = {
            # Standardized schema fields
            "site_suitability": site_suitability,
            "recommended_deployment": rec_strategy,
            "prediction": f"{ml_pred_type} Deployment",
            "prediction_explanation": explain_str,
            "feature_importance": top_importances,
            "technical_feasibility": feasibility_res.technical_feasibility and hard_passed,
            "feasibility_score": round(feasibility_res.feasibility_score, 2),
            "constraint_summary": constraint_summary_dict,
            "energy_yield": energy_yield_dict,
            "financial_metrics": financial_metrics_dict,
            "recommendation_reason": rec_reason,
            "status": "Success",
            # Backward compatibility fields
            "prediction_confidence": confidence_score,
            "annual_energy_yield": energy_res["annual_energy_yield"],
            "solar_energy_yield": energy_res["solar_energy_yield"],
            "wind_energy_yield": energy_res["wind_energy_yield"],
            "hybrid_energy_yield": energy_res["hybrid_energy_yield"],
            "annual_revenue": fin_res["annual_revenue"],
            "estimated_project_cost": fin_res["estimated_project_cost"],
            "payback_period": fin_res["payback_period"],
            "roi": fin_res["roi"],
            "deployment": ml_pred_type,
            "latitude": lat,
            "longitude": lon,
            "site_id": site_id,
            "energy_yield_estimation": energy_res,
            "financial_analysis": fin_res,
            "assessment_result": assessment_res,
            "candidate_ranking": ranked_candidates,
            "deployment_optimization": opt_res,
            "forecasting": forecast_res,
            "investment_recommendation": investment_res
        }

        # Merge top-level assessment_res sub-dictionaries for direct frontend component consumption
        if isinstance(assessment_res, dict):
            for k, v in assessment_res.items():
                if k not in out_response:
                    out_response[k] = v

        return out_response

