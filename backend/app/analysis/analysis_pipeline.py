from app.services.solar_service import SolarFeatureService
from app.services.wind_assessment import WindAssessmentService

from app.evaluation.evaluator import evaluate_site
from app.optimization.optimizer import DeploymentOptimizer

from app.services.energy_estimation import EnergyEstimationService

from app.feasibility.feasibility_engine import TechnicalFeasibilityEngine

from app.services.financial_analysis import FinancialAnalysisService

from app.ml.inference import ModelInference

from app.services.location_validation import validate_location


class AnalysisPipeline:
    """
    Complete renewable-energy site analysis pipeline.

    Workflow:

        Location
            ↓
        Location Validation
            ↓
        Environmental Data
            ↓
        Solar / Wind Assessment
            ↓
        Site Evaluation
            ↓
        Deployment Optimization
            ↓
        ML Prediction
            ↓
        Technical Feasibility
            ↓
        Energy Yield
            ↓
        Financial Analysis
            ↓
        Final Recommendation
    """

    def __init__(self):

        # -----------------------------------------------------
        # Services
        # -----------------------------------------------------

        self.solar_service = SolarFeatureService()

        self.wind_service = WindAssessmentService()

        self.optimizer = DeploymentOptimizer()

        self.energy_service = EnergyEstimationService()

        self.feasibility_engine = TechnicalFeasibilityEngine()

        self.model = ModelInference()

        self.financial_service = FinancialAnalysisService()

    # =========================================================
    # INVALID LOCATION RESPONSE
    # =========================================================

    def _invalid_location_response(
        self,
        latitude,
        longitude,
        location_validation
    ):
        """
        Return a clean response when the selected location
        is water or outside the supported analysis region.

        IMPORTANT:
        No ML, energy, financial or deployment calculation
        should happen for an invalid location.
        """

        reason = location_validation.get(
            "reason",
            "Selected location cannot be used for deployment."
        )

        return {

            # -------------------------------------------------
            # Location
            # -------------------------------------------------

            "location": {
                "latitude": latitude,
                "longitude": longitude
            },

            # -------------------------------------------------
            # Location validation
            # -------------------------------------------------

            "location_validation": location_validation,

            # -------------------------------------------------
            # Environmental data
            # -------------------------------------------------

            "environmental_data": {
                "solar_features": {},
                "wind_assessment": {}
            },

            # -------------------------------------------------
            # Site evaluation
            # -------------------------------------------------

            "site_evaluation": {

                "overall_score": 0,

                "recommendation": "Not Suitable",

                "remarks": [
                    reason
                ]
            },

            # -------------------------------------------------
            # Deployment
            # -------------------------------------------------

            "deployment_plan": {

                "recommended_technology": "None",

                "recommended_capacity_mw": 0,

                "expansion_status": "Not Applicable",

                "optimization_remarks": [
                    reason
                ]
            },

            # -------------------------------------------------
            # ML prediction
            # -------------------------------------------------

            "ml_prediction": {

                "prediction": 0,

                "status": "Rejected",

                "reason": reason
            },

            # -------------------------------------------------
            # Technical feasibility
            # -------------------------------------------------

            "technical_feasibility": {

                "hard_constraints": {

                    "passed": False,

                    "technical_feasibility":
                        "Not Technically Feasible",

                    "failed_constraints": [
                        reason
                    ]
                },

                "soft_constraints": {

                    "score": 0,

                    "remarks": []
                }
            },

            # -------------------------------------------------
            # Energy
            # -------------------------------------------------

            "energy_estimation": {

                "deployment_type": "None",

                "installed_capacity_mw": 0,

                "solar_capacity_factor": 0,

                "wind_capacity_factor": 0,

                "annual_solar_energy_mwh": 0,

                "annual_wind_energy_mwh": 0,

                "total_annual_energy_mwh": 0
            },

            # -------------------------------------------------
            # Financial analysis
            # -------------------------------------------------

            "financial_analysis": {

                "electricity_tariff_rs_per_kwh": 0,

                "annual_revenue_rs": 0,

                "estimated_project_cost_rs": 0,

                "payback_period_years": 0,

                "roi_percent": 0
            },

            # -------------------------------------------------
            # Final recommendation
            # -------------------------------------------------

            "final_recommendation":
                "Not Suitable for Deployment"
        }

    # =========================================================
    # MAIN ANALYSIS
    # =========================================================

    def analyze(
        self,
        latitude,
        longitude,
        land_area,
        available_land_percent,
        installed_capacity=100
    ):

        # =====================================================
        # 1. LOCATION VALIDATION
        # =====================================================

        location_validation = validate_location(
            latitude,
            longitude
        )

        # -----------------------------------------------------
        # STOP HERE if location is invalid / water
        # -----------------------------------------------------

        if not location_validation.get(
            "valid",
            False
        ):

            return self._invalid_location_response(
                latitude=latitude,
                longitude=longitude,
                location_validation=location_validation
            )

        # =====================================================
        # 2. SOLAR ENVIRONMENTAL DATA
        # =====================================================

        solar_features = (
            self.solar_service.get_solar_features(
                latitude,
                longitude
            )
        )

        # =====================================================
        # 3. WIND ASSESSMENT
        # =====================================================

        # Current wind value used by project.
        #
        # This can later be replaced with actual
        # Global Wind Atlas/API data.
        #
        wind_speed = 6.5

        wind_result = (
            self.wind_service.classify_wind_site(
                wind_speed
            )
        )

        # =====================================================
        # 4. SITE INFORMATION
        # =====================================================

        site = {

            "latitude": latitude,

            "longitude": longitude,

            "solar_irradiance":
                solar_features.get(
                    "solar_irradiance",
                    0
                ),

            "wind_speed":
                wind_speed,

            "slope": 2.1,

            "elevation": 120,

            "distance_to_grid": 1.8,

            "distance_to_road": 0.5
        }

        # =====================================================
        # 5. SITE EVALUATION
        # =====================================================

        evaluation = evaluate_site(
            1,
            site
        )

        # =====================================================
        # 6. DEPLOYMENT OPTIMIZATION
        # =====================================================

        plan = (
            self.optimizer.generate_deployment_plan(

                solar_score=85,

                wind_score=80,

                land_area=land_area,

                resource_score=85,

                available_land_percent=
                    available_land_percent
            )
        )

        # =====================================================
        # 7. MACHINE LEARNING PREDICTION
        # =====================================================

        features = [

            # Terrain
            site["slope"],

            site["elevation"],

            # Wind / weather
            15.0,                  # TurbulenceIntensity

            30.0,                  # AirTemperature

            65.0,                  # RelativeHumidity

            1200.0,                # Precipitation

            wind_speed,

            15.0,                  # WindGustSpeed

            1013.0,                # AirPressure

            # Solar
            solar_features.get(
                "solar_irradiance",
                0
            ),

            # Remote sensing
            0.45,                  # NDVI

            0.18,                  # NDBI

            0.10,                  # NDWI

            31.5,                  # LST

            # Geography
            site["elevation"],

            # Population / area
            1822695,

            4590
        ]

        prediction = self.model.predict_site(
            features
        )

        # =====================================================
        # 8. TECHNICAL FEASIBILITY
        # =====================================================

        feasibility = (
            self.feasibility_engine.evaluate({

                "solar_irradiance":
                    solar_features.get(
                        "solar_irradiance",
                        0
                    ),

                "wind_speed":
                    wind_speed,

                "slope":
                    site["slope"],

                "distance_to_grid":
                    site["distance_to_grid"],

                "distance_to_road":
                    site["distance_to_road"],

                "available_land_percent":
                    available_land_percent
            })
        )

        # =====================================================
        # 9. ENERGY YIELD
        # =====================================================

        energy = (
            self.energy_service.estimate_energy(

                site_result=evaluation,

                deployment_type=
                    plan.get(
                        "recommended_technology",
                        "Unknown"
                    ),

                installed_capacity=
                    installed_capacity,

                solar_irradiance=
                    solar_features.get(
                        "solar_irradiance",
                        0
                    ),

                wind_speed=
                    wind_speed
            )
        )

        # =====================================================
        # 10. FINANCIAL ANALYSIS
        # =====================================================

        financial_analysis = (
            self.financial_service.analyze_finances(

                installed_capacity=
                    installed_capacity,

                annual_energy_mwh=
                    energy.get(
                        "total_annual_energy_mwh",
                        0
                    )
            )
        )

        # =====================================================
        # 11. FINAL RECOMMENDATION
        # =====================================================

        hard_constraints = (
            feasibility.get(
                "hard_constraints",
                {}
            )
        )

        technical_feasible = (
            hard_constraints.get(
                "passed",
                False
            )
        )

        ml_suitable = (
            prediction.get(
                "prediction"
            ) == 1
        )

        site_suitable = (
            evaluation.get(
                "recommendation"
            ) == "Suitable"
        )

        # -----------------------------------------------------
        # Final decision
        # -----------------------------------------------------

        if (
            technical_feasible
            and ml_suitable
            and site_suitable
        ):

            final_recommendation = (
                "Suitable for Deployment"
            )

        elif site_suitable:

            final_recommendation = (
                "Conditionally Suitable"
            )

        else:

            final_recommendation = (
                "Not Suitable for Deployment"
            )

        # =====================================================
        # 12. RETURN COMPLETE RESULT
        # =====================================================

        return {

            # -------------------------------------------------
            # Location
            # -------------------------------------------------

            "location": {

                "latitude":
                    latitude,

                "longitude":
                    longitude
            },

            # -------------------------------------------------
            # Location validation
            # -------------------------------------------------

            "location_validation":
                location_validation,

            # -------------------------------------------------
            # Environmental data
            # -------------------------------------------------

            "environmental_data": {

                "solar_features":
                    solar_features,

                "wind_assessment":
                    wind_result
            },

            # -------------------------------------------------
            # Site evaluation
            # -------------------------------------------------

            "site_evaluation":
                evaluation,

            # -------------------------------------------------
            # Deployment
            # -------------------------------------------------

            "deployment_plan":
                plan,

            # -------------------------------------------------
            # ML prediction
            # -------------------------------------------------

            "ml_prediction":
                prediction,

            # -------------------------------------------------
            # Technical feasibility
            # -------------------------------------------------

            "technical_feasibility":
                feasibility,

            # -------------------------------------------------
            # Energy
            # -------------------------------------------------

            "energy_estimation":
                energy,

            # -------------------------------------------------
            # Financial
            # -------------------------------------------------

            "financial_analysis":
                financial_analysis,

            # -------------------------------------------------
            # Final recommendation
            # -------------------------------------------------

            "final_recommendation":
                final_recommendation
        }