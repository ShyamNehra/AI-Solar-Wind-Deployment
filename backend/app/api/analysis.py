from fastapi import APIRouter, Query, HTTPException

from app.analysis.analysis_pipeline import AnalysisPipeline
from app.schemas.analysis_response import AnalysisResponse

router = APIRouter()

pipeline = AnalysisPipeline()


@router.post(
    "/analysis",
    response_model=AnalysisResponse
)
def analyze_site(

    latitude: float = Query(
        ...,
        ge=-90,
        le=90
    ),

    longitude: float = Query(
        ...,
        ge=-180,
        le=180
    ),

    land_area: float = Query(
        ...,
        gt=0
    ),

    available_land_percent: float = Query(
        ...,
        ge=0,
        le=100
    ),

    installed_capacity: float = Query(
        100,
        gt=0
    )
):

    try:

        result = pipeline.analyze(

            latitude=latitude,

            longitude=longitude,

            land_area=land_area,

            available_land_percent=
                available_land_percent,

            installed_capacity=
                installed_capacity
        )

        site_evaluation = result.get(
            "site_evaluation",
            {}
        )

        deployment = result.get(
            "deployment_plan",
            {}
        )

        feasibility = result.get(
            "technical_feasibility",
            {}
        )

        hard_constraints = feasibility.get(
            "hard_constraints",
            {}
        )

        soft_constraints = feasibility.get(
            "soft_constraints",
            {}
        )

        energy = result.get(
            "energy_estimation",
            {}
        )

        financial = result.get(
            "financial_analysis",
            {}
        )

        location_validation = result.get(
            "location_validation",
            {}
        )

        recommendation_reason = []

        recommendation_reason.extend(
            site_evaluation.get(
                "remarks",
                []
            )
        )

        recommendation_reason.extend(
            hard_constraints.get(
                "failed_constraints",
                []
            )
        )

        recommendation_reason.extend(
            deployment.get(
                "optimization_remarks",
                []
            )
        )

        recommendation_reason.extend(
            soft_constraints.get(
                "remarks",
                []
            )
        )

        if location_validation.get("reason"):
            recommendation_reason.append(
                location_validation["reason"]
            )

        recommendation_reason = list(
            dict.fromkeys(
                recommendation_reason
            )
        )

        if not recommendation_reason:

            recommendation_reason.append(
                "Site analysis completed successfully."
            )

        # -----------------------------------------------------
        # FINAL RECOMMENDATION
        # -----------------------------------------------------

        if not location_validation.get(
            "valid",
            False
        ):

            final_recommendation = (
                "Not Suitable for Deployment"
            )

        elif not hard_constraints.get(
            "passed",
            False
        ):

            final_recommendation = (
                "Conditionally Suitable"
            )

        else:

            final_recommendation = (
                "Suitable for Deployment"
            )

        # -----------------------------------------------------
        # RESPONSE
        # -----------------------------------------------------

        return {

            "location": {

                "latitude":
                    latitude,

                "longitude":
                    longitude
            },

            "location_validation":
                location_validation,

            "environmental_data": {

                "solar_features":
                    result.get(
                        "environmental_data",
                        {}
                    ).get(
                        "solar_features",
                        result.get(
                            "solar_features",
                            {}
                        )
                    ),

                "wind_assessment":
                    result.get(
                        "environmental_data",
                        {}
                    ).get(
                        "wind_assessment",
                        result.get(
                            "wind_assessment",
                            {}
                        )
                    )
            },

            "site_suitability": {

                "overall_score":
                    site_evaluation.get(
                        "overall_score",
                        0
                    ),

                "recommendation":
                    site_evaluation.get(
                        "recommendation",
                        "Not Suitable"
                    )
            },

            "recommended_deployment": {

                "technology":
                    deployment.get(
                        "recommended_technology",
                        "None"
                    ),

                "capacity_mw":
                    deployment.get(
                        "recommended_capacity_mw",
                        0
                    ),

                "expansion_status":
                    deployment.get(
                        "expansion_status",
                        "Not Applicable"
                    )
            },

            "technical_feasibility": {

                "status":
                    hard_constraints.get(
                        "technical_feasibility",
                        "Not Technically Feasible"
                    ),

                "passed":
                    hard_constraints.get(
                        "passed",
                        False
                    ),

                "failed_constraints":
                    hard_constraints.get(
                        "failed_constraints",
                        []
                    ),

                "soft_constraint_score":
                    soft_constraints.get(
                        "score",
                        0
                    )
            },

            "energy_yield": {

                "annual_solar_energy_mwh":
                    energy.get(
                        "annual_solar_energy_mwh",
                        0
                    ),

                "annual_wind_energy_mwh":
                    energy.get(
                        "annual_wind_energy_mwh",
                        0
                    ),

                "total_annual_energy_mwh":
                    energy.get(
                        "total_annual_energy_mwh",
                        0
                    )
            },

            "financial_metrics": {

                "electricity_tariff_rs_per_kwh":
                    financial.get(
                        "electricity_tariff_rs_per_kwh",
                        0
                    ),

                "annual_revenue_rs":
                    financial.get(
                        "annual_revenue_rs",
                        0
                    ),

                "estimated_project_cost_rs":
                    financial.get(
                        "estimated_project_cost_rs",
                        0
                    ),

                "payback_period_years":
                    financial.get(
                        "payback_period_years",
                        0
                    ),

                "roi_percent":
                    financial.get(
                        "roi_percent",
                        0
                    )
            },

            "recommendation_reason":
                recommendation_reason,

            "final_recommendation":
                final_recommendation
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,

            detail=
                f"Analysis failed: {str(e)}"
        )