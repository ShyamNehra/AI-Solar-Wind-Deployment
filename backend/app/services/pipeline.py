from app.services.inference import predict_solar_radiation
from app.services.scoring import calculate_category_scores, calculate_overall_score
from app.services.optimization import generate_deployment_plan
from app.services.financials import estimate_energy_yield, calculate_financials

def run_site_analysis_pipeline(
    latitude: float,
    longitude: float,
    area_sq_m: float,
    electricity_tariff_inr_kwh: float,
    month: int = 6,
    day: int = 15,
    temp_c: float = 28.0,
    wind_speed_ms: float = 6.5,
    slope_deg: float = 2.5,
    elevation_m: float = 920.0,
    dist_grid_m: float = 1200.0,
    dist_road_m: float = 400.0
):
    """
    Executes the complete end-to-end solar-wind site suitability, ML prediction, feasibility, and financial pipeline.
    """
    # 1. Run Machine Learning solar prediction
    ml_result = predict_solar_radiation(month, day, temp_c, wind_speed_ms)
    predicted_ghi = ml_result["predicted_ghi"]
    
    # 2. Category-wise Scoring
    category_scores = calculate_category_scores(
        solar_irr=predicted_ghi,
        wind_speed=wind_speed_ms,
        slope=slope_deg,
        elevation=elevation_m,
        dist_grid=dist_grid_m,
        dist_road=dist_road_m
    )
    
    # 3. Overall Score
    overall_score = calculate_overall_score(category_scores)
    
    # 4. Technical Feasibility & Deployment Plan (Hard & Soft Constraints)
    deployment_plan = generate_deployment_plan(
        slope=slope_deg,
        elevation=elevation_m,
        dist_grid=dist_grid_m,
        dist_road=dist_road_m,
        area_sq_m=area_sq_m,
        solar_score=category_scores["renewable_resource_score"],
        wind_score=category_scores["renewable_resource_score"] # using resource index
    )
    
    # 5. Energy Yield Estimation
    energy_yield = estimate_energy_yield(
        strategy=deployment_plan["recommended_technology"],
        capacity_mw=deployment_plan["recommended_capacity_mw"],
        solar_irr=predicted_ghi,
        wind_speed=wind_speed_ms
    )
    
    # 6. Financial Metrics Analysis
    financials = calculate_financials(
        yield_kwh=energy_yield,
        strategy=deployment_plan["recommended_technology"],
        capacity_mw=deployment_plan["recommended_capacity_mw"],
        tariff_inr_kwh=electricity_tariff_inr_kwh
    )
    
    # Consolidated return model
    return {
        "location": {
            "latitude": latitude,
            "longitude": longitude,
            "area_sq_m": area_sq_m
        },
        "ml_predictions": {
            "predicted_ghi_kwh_m2_day": predicted_ghi,
            "feature_importance": ml_result["explanation"]
        },
        "scoring": {
            "category_scores": category_scores,
            "overall_suitability_score": overall_score
        },
        "technical_assessment": {
            "technical_feasibility": deployment_plan["technical_feasibility"],
            "recommended_deployment": deployment_plan["recommended_technology"],
            "recommended_capacity_mw": deployment_plan["recommended_capacity_mw"],
            "expansion_status": deployment_plan["expansion_status"],
            "remarks": deployment_plan["remarks"]
        },
        "energy": {
            "annual_energy_yield_kwh": energy_yield
        },
        "financials": financials
    }
