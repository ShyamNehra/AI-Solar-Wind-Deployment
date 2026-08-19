import math
from sqlalchemy.orm import Session
from app.db.mongo import raw_environmental_cache
from app.models.environmental import SiteEnvironmentalData
from app.models.solar_prediction import SolarPrediction
from app.models.wind_prediction import WindPrediction
from app.models.energy_forecast import EnergyForecast
from app.models.site import Site
from app.connectors.nasa_power import fetch_solar_data
from app.connectors.open_meteo_historical import fetch_historical_wind_data
from app.ml.solar_model import predict_solar_potential, SOLAR_PARAMETERS
from app.ml.wind_model import predict_wind_potential

MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
DAYS_IN_MONTH = {
    "JAN": 31, "FEB": 28.25, "MAR": 31, "APR": 30, "MAY": 31, "JUN": 30,
    "JUL": 31, "AUG": 31, "SEP": 30, "OCT": 31, "NOV": 30, "DEC": 31
}

FORECAST_FORMULA_USED = "Solar monthly kWh = monthly_irradiance * days * panel_efficiency * performance_ratio * panel_area_per_kwp_sqm; Wind monthly kWh = turbine_capacity * hours * monthly_capacity_factor"
FORECAST_FORMULA_SOURCE = "Solar formula: NREL Standard PV performance metrics; Wind formula: Rayleigh-CDF aerodynamic power curves"
DEGRADATION_RATE_SOURCE = "Solar: NREL PV Degradation Rates Study (2012); Wind: Staffell & Green Turbine Aging Performance Study (2014)"
ELECTRICITY_RATE_SOURCE = "U.S. Energy Information Administration (EIA) Electric Power Monthly published average retail rate (https://www.eia.gov/)"
GRID_CONTRIBUTION_NOTE = "Illustrative grid contribution ratio calculated using expected annual energy output divided by a regional baseline demand of 10,000,000 kWh/year. This is a proxy model pending real utility-scale grid baseline integration."

def get_or_create_predictions(site_id: int, db: Session):
    """
    Ensure predictions exist for the site. If missing, generate and persist them.
    """
    env_data = db.query(SiteEnvironmentalData).filter(SiteEnvironmentalData.site_id == site_id).first()
    if not env_data:
        raise ValueError("Environmental data not refreshed yet.")
        
    solar_pred = db.query(SolarPrediction).filter(SolarPrediction.site_id == site_id).order_by(SolarPrediction.created_at.desc()).first()
    if not solar_pred:
        res = predict_solar_potential(env_data.average_solar_irradiance)
        solar_pred = SolarPrediction(
            site_id=site_id,
            annual_irradiance=res["annual_irradiance"],
            peak_sun_hours=res["peak_sun_hours"],
            expected_energy_output=res["expected_energy_output"],
            capacity_factor=res["capacity_factor"],
            performance_ratio=res["performance_ratio"]
        )
        db.add(solar_pred)
        db.commit()
        db.refresh(solar_pred)

    wind_pred = db.query(WindPrediction).filter(WindPrediction.site_id == site_id).order_by(WindPrediction.created_at.desc()).first()
    if not wind_pred:
        res = predict_wind_potential(env_data.average_wind_speed)
        wind_pred = WindPrediction(
            site_id=site_id,
            average_wind_speed=res["average_wind_speed"],
            wind_power_density=res["wind_power_density"],
            turbulence_intensity=res["turbulence_intensity"],
            capacity_factor=res["capacity_factor"],
            expected_annual_energy_production=res["expected_annual_energy_production"]
        )
        db.add(wind_pred)
        db.commit()
        db.refresh(wind_pred)

    return env_data, solar_pred, wind_pred

def generate_seasonal_forecast(site_id: int, db: Session) -> dict:
    env_data, _, _ = get_or_create_predictions(site_id, db)
    site = db.query(Site).filter(Site.id == site_id).first()
    lat, lon = site.elevation, 0.0 # coordinates resolved from geometry
    from geoalchemy2.shape import to_shape
    geom = to_shape(site.geom)
    lat, lon = geom.y, geom.x
    
    # 1. Fetch cached Solar payload
    lat_key = round(lat, 4)
    lon_key = round(lon, 4)
    solar_cache = raw_environmental_cache.find_one({"lat": lat_key, "lon": lon_key, "source": "nasa_power"})
    if not solar_cache:
        payload = fetch_solar_data(lat, lon)
        raw_environmental_cache.update_one(
            {"lat": lat_key, "lon": lon_key, "source": "nasa_power"},
            {"$set": {"payload": payload}},
            upsert=True
        )
        solar_payload = payload
    else:
        solar_payload = solar_cache["payload"]
        
    solar_params = solar_payload["properties"]["parameter"]["ALLSKY_SFC_SW_DWN"]
    
    # Calculate Solar monthly energy (kWh/month) for a 1.0 kWp reference system
    solar_seasonal = {}
    eff = SOLAR_PARAMETERS["panel_efficiency"]
    pr = SOLAR_PARAMETERS["performance_ratio"]
    area = SOLAR_PARAMETERS["panel_area_per_kwp_sqm"]
    for m in MONTHS:
        val = solar_params[m]
        # output = irradiance (kWh/m2/day) * days * efficiency * performance_ratio * area * 1.0 kWp
        solar_seasonal[m] = round(val * DAYS_IN_MONTH[m] * eff * pr * area, 2)
        
    # 2. Fetch cached Wind payload
    wind_cache = raw_environmental_cache.find_one({"lat": lat_key, "lon": lon_key, "source": "open_meteo_wind"})
    if not wind_cache:
        payload = fetch_historical_wind_data(lat, lon)
        raw_environmental_cache.update_one(
            {"lat": lat_key, "lon": lon_key, "source": "open_meteo_wind"},
            {"$set": {"payload": payload}},
            upsert=True
        )
        wind_payload = payload
    else:
        wind_payload = wind_cache["payload"]
        
    # Group hourly wind speeds by month
    time_series = wind_payload["hourly"]["time"]
    wind_speeds = wind_payload["hourly"]["wind_speed_10m"]
    wind_dirs = wind_payload["hourly"]["wind_direction_10m"]
    
    month_speeds = {m: [] for m in MONTHS}
    for t_str, speed in zip(time_series, wind_speeds):
        # Format is "YYYY-MM-DDTHH:MM"
        month_idx = int(t_str[5:7])
        m_str = MONTHS[month_idx - 1]
        if speed is not None:
            month_speeds[m_str].append(speed)
            
    # Calculate Wind monthly energy (kWh/month) for a 2000 kW reference turbine
    wind_seasonal = {}
    for m in MONTHS:
        speeds = month_speeds[m]
        avg_v = sum(speeds) / len(speeds) if speeds else 0.0
        # Call wind prediction logic
        pred = predict_wind_potential(avg_v)
        cf = pred["capacity_factor"]
        # Output = Capacity (2000 kW) * hours in month * capacity factor
        hours = DAYS_IN_MONTH[m] * 24.0
        wind_seasonal[m] = round(2000.0 * hours * cf, 2)
        
    # Retrieve or create EnergyForecast record in Postgres
    forecast_rec = db.query(EnergyForecast).filter(EnergyForecast.site_id == site_id).first()
    if not forecast_rec:
        forecast_rec = EnergyForecast(site_id=site_id)
        db.add(forecast_rec)
        
    forecast_rec.solar_seasonal_kwh = solar_seasonal
    forecast_rec.wind_seasonal_kwh = wind_seasonal
    db.commit()
    db.refresh(forecast_rec)
    
    return {
        "site_id": site_id,
        "solar_seasonal_kwh": solar_seasonal,
        "wind_seasonal_kwh": wind_seasonal,
        "formula_used": FORECAST_FORMULA_USED,
        "formula_source": FORECAST_FORMULA_SOURCE
    }

def generate_longterm_projection(site_id: int, db: Session) -> dict:
    _, solar_pred, wind_pred = get_or_create_predictions(site_id, db)
    
    # Degradation rates
    # Solar: 0.5% per year (NREL PV lifetime study: "Photovoltaic Degradation Rates — An Analytical Review", 2012)
    # Wind: 1.5% per year (Staffell & Green wind age degradation study: "How does wind farm performance decline with age?", 2014)
    degradation_solar = 0.005
    degradation_wind = 0.015
    
    solar_y1 = solar_pred.expected_energy_output
    wind_y1 = wind_pred.expected_annual_energy_production
    
    solar_longterm = []
    wind_longterm = []
    
    for year in range(1, 21):
        solar_val = round(solar_y1 * ((1 - degradation_solar) ** (year - 1)), 2)
        wind_val = round(wind_y1 * ((1 - degradation_wind) ** (year - 1)), 2)
        solar_longterm.append(solar_val)
        wind_longterm.append(wind_val)
        
    # Persist to database
    forecast_rec = db.query(EnergyForecast).filter(EnergyForecast.site_id == site_id).first()
    if not forecast_rec:
        forecast_rec = EnergyForecast(site_id=site_id)
        db.add(forecast_rec)
        
    forecast_rec.solar_longterm_kwh = solar_longterm
    forecast_rec.wind_longterm_kwh = wind_longterm
    db.commit()
    db.refresh(forecast_rec)
    
    return {
        "site_id": site_id,
        "solar_longterm_kwh": solar_longterm,
        "wind_longterm_kwh": wind_longterm,
        "degradation_rate_solar": degradation_solar,
        "degradation_rate_wind": degradation_wind,
        "degradation_rate_source": DEGRADATION_RATE_SOURCE
    }

def generate_revenue_forecast(site_id: int, db: Session) -> dict:
    _, solar_pred, wind_pred = get_or_create_predictions(site_id, db)
    
    # EIA Average retail price of electricity (published in EIA Electric Power Monthly): $0.125 / kWh
    rate = 0.125
    rate_source = ELECTRICITY_RATE_SOURCE
    
    solar_y1 = solar_pred.expected_energy_output
    wind_y1 = wind_pred.expected_annual_energy_production
    
    solar_rev = round(solar_y1 * rate, 2)
    wind_rev = round(wind_y1 * rate, 2)
    combined_rev = round((solar_y1 + wind_y1) * rate, 2)
    
    # Grid contribution ratio: expected annual energy output / 10 GWh regional baseline
    baseline_kwh = 10000000.0  # 10,000,000 kWh baseline
    combined_output = solar_y1 + wind_y1
    grid_ratio = round(combined_output / baseline_kwh, 6)
    grid_note = GRID_CONTRIBUTION_NOTE
    
    # Persist to database
    forecast_rec = db.query(EnergyForecast).filter(EnergyForecast.site_id == site_id).first()
    if not forecast_rec:
        forecast_rec = EnergyForecast(site_id=site_id)
        db.add(forecast_rec)
        
    forecast_rec.solar_annual_revenue = solar_rev
    forecast_rec.wind_annual_revenue = wind_rev
    forecast_rec.combined_annual_revenue = combined_rev
    forecast_rec.electricity_rate_usd_kwh = rate
    forecast_rec.grid_contribution_ratio = grid_ratio
    forecast_rec.grid_contribution_note = grid_note
    db.commit()
    db.refresh(forecast_rec)
    
    return {
        "site_id": site_id,
        "solar_annual_revenue": solar_rev,
        "wind_annual_revenue": wind_rev,
        "combined_annual_revenue": combined_rev,
        "electricity_rate_usd_kwh": rate,
        "electricity_rate_source": rate_source,
        "grid_contribution_ratio": grid_ratio,
        "grid_contribution_note": grid_note
    }
