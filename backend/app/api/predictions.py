from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.postgres import get_db
from app.models.site import Site
from app.models.environmental import SiteEnvironmentalData
from app.models.solar_prediction import SolarPrediction
from app.models.wind_prediction import WindPrediction
from app.models.user import User
from app.api.dependencies import get_current_user
from app.ml.solar_model import predict_solar_potential
from app.ml.wind_model import predict_wind_potential
from app.schemas.predictions import SolarPredictionOut, WindPredictionOut

router = APIRouter(prefix="/sites", tags=["Predictions"])

SOLAR_PRED_DATA_SOURCE = "NASA POWER Climatology"
SOLAR_PRED_FORMULA_USED = "Expected Annual Energy Output = Annual Incident Irradiance * panel_efficiency * performance_ratio * panel_area_per_kwp_sqm"
SOLAR_PRED_FORMULA_SOURCE = "NREL PV performance metrics (https://www.nrel.gov/docs/fy14osti/62641.pdf)"
SOLAR_CAP_FACTOR_NOTE = "This is a placeholder capacity factor calculated using the standard formula CF = expected_energy_output / (8766 * system_size_kwp). Detailed capacity factor calculations based on ambient temperature coefficients and specific inverter efficiency curves are deferred until module specification datasheets are uploaded."
SOLAR_MODEL_NOTE = "This is a documented physics-based performance model. Supervised ML model training (e.g. XGBoost) is deferred until actual solar generation production target data becomes available for this site."

WIND_PRED_DATA_SOURCE = "Open-Meteo Historical Weather API"
WIND_PRED_FORMULA_USED = "Wind Power Density (WPD) = 0.5 * air_density * wind_speed^3"
WIND_PRED_FORMULA_SOURCE = "Standard Wind Aerodynamics Equations with Open-Meteo Historical Climatology (Rayleigh CF approximation)"
WIND_CAP_FACTOR_NOTE = "This is a Rayleigh-CDF-derived capacity factor assuming cut-in = 3.0 m/s, cut-out = 25.0 m/s, and a 45% power curve discount efficiency factor. This calculation is a simplified statistical placeholder pending real turbine-specific power curve data."
WIND_TURB_FORMULA_USED = "Turbulence Intensity (TI) = 0.12 (assumed constant baseline value)"
WIND_TURB_FORMULA_SOURCE = "Standard default assumption for flat/desert terrain in the absence of high-frequency anemometer time-series data"
WIND_MODEL_NOTE = "This is a documented physics-based aerodynamic model. Time-series ML model training (e.g. LSTM or Prophet) is deferred until actual wind generation production target data becomes available for this site."

@router.post("/{site_id}/predictions/solar", response_model=SolarPredictionOut)
def run_solar_prediction(
    site_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Retrieve site
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")
        
    # Check permissions
    project = site.project
    user_roles = [role.name for role in current_user.roles]
    if "Administrator" not in user_roles and project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
    # 2. Retrieve environmental data
    env_data = db.query(SiteEnvironmentalData).filter(SiteEnvironmentalData.site_id == site_id).first()
    if not env_data or env_data.average_solar_irradiance is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Environmental data has not been fetched yet. Please refresh environmental data for this site first."
        )
        
    # 3. Call prediction function
    pred_res = predict_solar_potential(env_data.average_solar_irradiance)
    
    # 4. Persist to Postgres database
    prediction = SolarPrediction(
        site_id=site_id,
        annual_irradiance=pred_res["annual_irradiance"],
        peak_sun_hours=pred_res["peak_sun_hours"],
        expected_energy_output=pred_res["expected_energy_output"],
        capacity_factor=pred_res["capacity_factor"],
        performance_ratio=pred_res["performance_ratio"]
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    
    return SolarPredictionOut(
        id=prediction.id,
        site_id=prediction.site_id,
        annual_irradiance=prediction.annual_irradiance,
        peak_sun_hours=prediction.peak_sun_hours,
        expected_energy_output=prediction.expected_energy_output,
        capacity_factor=prediction.capacity_factor,
        performance_ratio=prediction.performance_ratio,
        model_type=pred_res["model_type"],
        data_source=SOLAR_PRED_DATA_SOURCE,
        formula_used=SOLAR_PRED_FORMULA_USED,
        formula_source=SOLAR_PRED_FORMULA_SOURCE,
        capacity_factor_note=SOLAR_CAP_FACTOR_NOTE,
        is_trained_ml_model=False,
        model_note=SOLAR_MODEL_NOTE,
        created_at=prediction.created_at
    )

@router.post("/{site_id}/predictions/wind", response_model=WindPredictionOut)
def run_wind_prediction(
    site_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Retrieve site
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")
        
    # Check permissions
    project = site.project
    user_roles = [role.name for role in current_user.roles]
    if "Administrator" not in user_roles and project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
    # 2. Retrieve environmental data
    env_data = db.query(SiteEnvironmentalData).filter(SiteEnvironmentalData.site_id == site_id).first()
    if not env_data or env_data.average_wind_speed is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Environmental data has not been fetched yet. Please refresh environmental data for this site first."
        )
        
    # 3. Call prediction function
    pred_res = predict_wind_potential(env_data.average_wind_speed)
    
    # 4. Persist to Postgres database
    prediction = WindPrediction(
        site_id=site_id,
        average_wind_speed=pred_res["average_wind_speed"],
        wind_power_density=pred_res["wind_power_density"],
        turbulence_intensity=pred_res["turbulence_intensity"],
        capacity_factor=pred_res["capacity_factor"],
        expected_annual_energy_production=pred_res["expected_annual_energy_production"]
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    
    return WindPredictionOut(
        id=prediction.id,
        site_id=prediction.site_id,
        average_wind_speed=prediction.average_wind_speed,
        wind_power_density=prediction.wind_power_density,
        turbulence_intensity=prediction.turbulence_intensity,
        capacity_factor=prediction.capacity_factor,
        expected_annual_energy_production=prediction.expected_annual_energy_production,
        model_type=pred_res["model_type"],
        data_source=WIND_PRED_DATA_SOURCE,
        formula_used=WIND_PRED_FORMULA_USED,
        formula_source=WIND_PRED_FORMULA_SOURCE,
        capacity_factor_note=WIND_CAP_FACTOR_NOTE,
        turbulence_formula_used=WIND_TURB_FORMULA_USED,
        turbulence_formula_source=WIND_TURB_FORMULA_SOURCE,
        is_trained_ml_model=False,
        model_note=WIND_MODEL_NOTE,
        created_at=prediction.created_at
    )
